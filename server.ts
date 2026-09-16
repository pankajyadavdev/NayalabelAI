import express from "express";
import cors from "cors";
import path from "path";
import fs from "fs";
import multer from "multer";
import crypto from "crypto";

import companiesData from "./src/data/companies.json";
import { LegalMetrologyRulesEngine } from "./src/rulesEngine";
import { LabelOCRService } from "./src/ocrService";
import { generatePdfReport } from "./src/pdfReport";
import { dbStore, STANDARD_PRODUCTS, USERS } from "./src/database";

const app = express();
const PORT = Number(process.env.PORT) || 3000;

// Ensure uploads folder exists
const uploadsDir = path.join(process.cwd(), "uploads");
if (!fs.existsSync(uploadsDir)) {
  fs.mkdirSync(uploadsDir, { recursive: true });
}

// Multer for file uploads
const storage = multer.diskStorage({
  destination: (req, file, cb) => cb(null, uploadsDir),
  filename: (req, file, cb) => {
    const ext = path.extname(file.originalname) || ".jpg";
    const rand = crypto.randomBytes(4).toString("hex").toUpperCase();
    cb(null, `scan_${Date.now()}_${rand}${ext}`);
  }
});
const upload = multer({
  storage,
  limits: { fileSize: 25 * 1024 * 1024 }
});

// Middleware
app.use(cors());
app.use(express.json({ limit: "50mb" }));
app.use(express.urlencoded({ extended: true, limit: "50mb" }));

// Initialize services
const rulesEngine = new LegalMetrologyRulesEngine(companiesData as any);
const ocrService = new LabelOCRService();

// ================= API ROUTES =================

// Health check
app.get("/api/health", (req, res) => {
  res.json({ status: "ok", timestamp: new Date().toISOString() });
});

// Auth endpoints
app.post("/api/auth/login", (req, res) => {
  const { username, password } = req.body || {};
  const user = USERS.find(u => u.username === username);

  if (!user || password !== `${username}123`) {
    // Also accept simple login for officer/manager/admin
    if (username === "officer" || username === "manager" || username === "admin") {
      const found = USERS.find(u => u.username === username)!;
      return res.json({
        access_token: `nyaya-jwt-token-${username}-${Date.now()}`,
        token_type: "bearer",
        user: found
      });
    }
    return res.status(401).json({ detail: "Invalid username or credentials." });
  }

  return res.json({
    access_token: `nyaya-jwt-token-${user.username}-${Date.now()}`,
    token_type: "bearer",
    user
  });
});

app.get("/api/auth/me", (req, res) => {
  res.json(USERS[0]);
});

app.post("/api/auth/logout", (req, res) => {
  res.json({ message: "Logged out successfully" });
});

// Products & Companies
app.get("/api/products", (req, res) => {
  res.json({ products: STANDARD_PRODUCTS });
});

app.get("/api/companies", (req, res) => {
  res.json({ companies: companiesData });
});

// Analytics Dashboard
app.get("/api/analytics/dashboard", (req, res) => {
  const stats = dbStore.getDashboardStats();
  res.json(stats);
});

// Inspection History
app.get("/api/history", (req, res) => {
  const items = dbStore.getAllScans();
  res.json({ items, total: items.length });
});

// Get Scan Details
app.get("/api/scan/:scan_id", (req, res) => {
  const scan = dbStore.getScanById(req.params.scan_id);
  if (!scan) {
    return res.status(404).json({ detail: `Inspection record '${req.params.scan_id}' not found.` });
  }
  res.json(scan);
});

// AI Product Detection
app.post("/api/scan/detect-product", upload.single("image") as any, async (req, res) => {
  try {
    let filepath = "";

    if (req.file) {
      filepath = req.file.path;
    } else if (req.body.image_base64) {
      const b64Data = req.body.image_base64.replace(/^data:image\/\w+;base64,/, "");
      const buffer = Buffer.from(b64Data, "base64");
      const filename = `detect_${Date.now()}_${crypto.randomBytes(3).toString("hex")}.jpg`;
      filepath = path.join(uploadsDir, filename);
      fs.writeFileSync(filepath, buffer);
    } else if (req.body.product_name) {
      filepath = req.body.product_name;
    }

    const detection = await ocrService.detectProductIdentity(filepath || "kurkure");
    res.json(detection);
  } catch (err: any) {
    console.error("AI detection route error:", err);
    res.status(500).json({ detail: "AI product detection error: " + err.message });
  }
});

// Scan Upload and Execute Inspection
app.post("/api/scan/upload", upload.single("image") as any, async (req, res) => {
  try {
    let savedFilename = "";
    let filepath = "";

    if (req.file) {
      savedFilename = req.file.filename;
      filepath = req.file.path;
    } else if (req.body.image_base64) {
      const b64Data = req.body.image_base64.replace(/^data:image\/\w+;base64,/, "");
      const buffer = Buffer.from(b64Data, "base64");
      savedFilename = `scan_NYAYA-${Date.now().toString().slice(-6)}.jpg`;
      filepath = path.join(uploadsDir, savedFilename);
      fs.writeFileSync(filepath, buffer);
    } else {
      savedFilename = `synthetic_scan_${Date.now()}.jpg`;
      filepath = path.join(uploadsDir, savedFilename);
      // Create empty placeholder file if needed
      if (!fs.existsSync(filepath)) {
        fs.writeFileSync(filepath, Buffer.from([]));
      }
    }

    const requestedProduct = req.body.product_name || "AUTO";
    const pdpArea = parseFloat(req.body.pdp_area_sq_cm || "150.0") || 150.0;

    // Dynamic AI vision extraction directly from the uploaded/captured image
    const extracted = await ocrService.extractFromImage(filepath, pdpArea);

    const isNonPackaged =
      extracted.is_packaged_product === false ||
      (typeof extracted.detected_object_type === "string" &&
        (extracted.detected_object_type.includes("HAND") ||
         extracted.detected_object_type.includes("FACE") ||
         extracted.detected_object_type.includes("PERSON") ||
         extracted.detected_object_type.includes("BODY") ||
         extracted.detected_object_type.includes("FINGER") ||
         extracted.detected_object_type.includes("SKIN") ||
         extracted.detected_object_type.includes("NON_PACKAGED"))) ||
      (typeof extracted.commodity_name === "string" &&
        (extracted.commodity_name.toLowerCase().includes("hand") ||
         extracted.commodity_name.toLowerCase().includes("face") ||
         extracted.commodity_name.toLowerCase().includes("non-packaged")));

    let finalProductName = "";
    let finalBrand = "";
    let finalCompany = "";

    if (isNonPackaged) {
      finalProductName = extracted.commodity_name && !extracted.commodity_name.toLowerCase().includes("packaged food")
        ? extracted.commodity_name
        : (extracted.detected_object_type ? extracted.detected_object_type.replace(/_/g, " ") : "Human Hand / Non-Packaged Target");
      finalBrand = "N/A (Non-Packaged)";
      finalCompany = "Non-Packaged Target (No Packer Registered)";
    } else {
      finalProductName = extracted.commodity_name || requestedProduct || "Packaged Food Commodity";
      finalBrand = extracted.brand_name || "FMCG Brand";
      finalCompany = "Registered FMCG Packer";

      const matchedComp = rulesEngine.findMatchingFMCGCompany(extracted.manufacturer_name_and_address || extracted.commodity_name);
      if (matchedComp) {
        finalCompany = matchedComp.name;
      } else if (extracted.manufacturer_name_and_address) {
        finalCompany = extracted.manufacturer_name_and_address.split(",")[0].trim();
      }
    }

    const evalResult = rulesEngine.evaluateCompliance(extracted, pdpArea);

    const now = new Date();
    const h = now.getHours();
    const h12 = h % 12 || 12;
    const ampm = h >= 12 ? "pm" : "am";
    const mStr = String(now.getMinutes()).padStart(2, "0");
    const sStr = String(now.getSeconds()).padStart(2, "0");
    const formattedTs = `${now.getMonth() + 1}/${now.getDate()}/${now.getFullYear()}, ${h12}:${mStr}:${sStr} ${ampm}`;

    const randHex = crypto.randomBytes(3).toString("hex").toUpperCase();
    const scanId = `NYAYA-${now.getFullYear()}-${randHex}`;

    let officerNote = "Routine statutory compliance inspection conducted under Legal Metrology Act 2009.";
    if (extracted.is_packaged_product === false) {
      officerNote = extracted.non_packaged_warning || "WARNING: Non-packaged item detected. Section 18 applies to pre-packaged commodities.";
    } else if (evalResult.violations && evalResult.violations.length > 0) {
      officerNote = `Notice issued for ${evalResult.violations.length} statutory violation(s) (${evalResult.missing_count || 0} missing, ${evalResult.non_compliant_count || 0} non-compliant). Re-inspection required under Section 36.`;
    }

    const newScan = dbStore.addScan({
      scan_id: scanId,
      product: finalProductName,
      product_name: finalProductName,
      brand_name: finalBrand,
      company_name: finalCompany,
      image_filename: savedFilename,
      image_url: `/uploads/${savedFilename}`,
      image_path: filepath,
      is_packaged_product: !isNonPackaged,
      object_category: isNonPackaged ? (extracted.detected_object_type || "HUMAN_HAND_OR_NON_PACKAGED") : "PACKAGED_FOOD_COMMODITY",
      warning_message: isNonPackaged ? (extracted.non_packaged_warning || evalResult.warning_message) : undefined,
      missing_count: evalResult.missing_count,
      non_compliant_count: evalResult.non_compliant_count,
      pdp_area_sq_cm: pdpArea,
      status: evalResult.status,
      overall_status: evalResult.status,
      risk_score: evalResult.risk_score.toFixed(2),
      compliance_score: evalResult.compliance_score,
      violations_count: evalResult.violations.length,
      extracted_data: extracted,
      evaluation_result: evalResult,
      officer_notes: officerNote,
      inspector_id: "LMO-DL-7729",
      timestamp: formattedTs,
      created_at: now.toISOString()
    });

    res.json(newScan);
  } catch (err: any) {
    console.error("Scan upload error:", err);
    res.status(500).json({ detail: "Error processing packaging inspection: " + err.message });
  }
});

// Reset Benchmark Database
app.post("/api/scan/reset-benchmark", (req, res) => {
  dbStore.seedBenchmarkData();
  res.json({ message: "Benchmark database restored successfully", total_scans: 14 });
});

// Download PDF Report
app.get("/api/scan/:scan_id/pdf", async (req, res) => {
  try {
    const scan = dbStore.getScanById(req.params.scan_id);
    if (!scan) {
      return res.status(404).send("Inspection record not found");
    }

    res.setHeader("Content-Type", "application/pdf");
    res.setHeader("Content-Disposition", `inline; filename="NyayLabel_Report_${scan.scan_id}.pdf"`);

    await generatePdfReport(scan, res);
  } catch (err: any) {
    console.error("PDF generation error:", err);
    if (!res.headersSent) {
      res.status(500).send("Error generating PDF inspection report: " + err.message);
    }
  }
});

// Download JSON Report
app.get("/api/scan/:scan_id/json", (req, res) => {
  const scan = dbStore.getScanById(req.params.scan_id);
  if (!scan) {
    return res.status(404).json({ detail: "Inspection record not found" });
  }
  res.setHeader("Content-Disposition", `attachment; filename="NyayLabel_Audit_${scan.scan_id}.json"`);
  res.json(scan);
});

// Static assets
app.use(express.static(path.join(process.cwd(), "frontend")));
app.use("/uploads", express.static(uploadsDir));

// Fallback to frontend index.html
app.get("*", (req, res) => {
  res.sendFile(path.join(process.cwd(), "frontend", "index.html"));
});

// Start Server
app.listen(PORT, "0.0.0.0", () => {
  console.log(`NyayLabel AI compliance server running on http://0.0.0.0:${PORT}`);
});
