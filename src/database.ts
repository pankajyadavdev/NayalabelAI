import companiesData from "./data/companies.json";
import { LegalMetrologyRulesEngine } from "./rulesEngine";

export interface User {
  id: number;
  username: string;
  hashed_password?: string;
  role: string;
  full_name: string;
  department: string;
  badge_number: string;
  created_at: string;
}

export interface ProductScan {
  id: number;
  display_id: string;
  scan_id: string;
  product: string;
  product_name: string;
  brand_name: string;
  company_name: string;
  image_filename?: string;
  image_url?: string;
  image_path?: string;
  is_packaged_product?: boolean;
  object_category?: string;
  warning_message?: string;
  missing_count?: number;
  non_compliant_count?: number;
  pdp_area_sq_cm: number;
  status: string; // Passed, Failed, Review Required
  overall_status: string;
  risk_score: string; // "0.93", "0.00", etc.
  compliance_score: number;
  violations_count: number;
  extracted_data: Record<string, any>;
  evaluation_result: Record<string, any>;
  officer_notes: string;
  inspector_id: string;
  timestamp: string;
  created_at: string;
}

export const USERS: User[] = [
  {
    id: 1,
    username: "officer",
    role: "ENFORCEMENT_OFFICER",
    full_name: "R. K. Sharma (LMO)",
    department: "Directorate of Legal Metrology, Delhi",
    badge_number: "LMO-DL-7729",
    created_at: new Date().toISOString()
  },
  {
    id: 2,
    username: "manager",
    role: "BRAND_MANAGER",
    full_name: "Pooja Verma",
    department: "Regulatory Compliance & Quality Assurance",
    badge_number: "FMCG-QA-4012",
    created_at: new Date().toISOString()
  },
  {
    id: 3,
    username: "admin",
    role: "ADMIN",
    full_name: "Dr. A. K. Mathur",
    department: "Ministry of Consumer Affairs",
    badge_number: "MCA-DIR-001",
    created_at: new Date().toISOString()
  }
];

export const STANDARD_PRODUCTS = [
  {
    id: "kurkure_schezwan",
    name: "Kurkure Schezwan (75g)",
    brand: "Kurkure",
    company: "PepsiCo India Holdings Pvt. Ltd.",
    category: "Extruded Snacks",
    pdp_area_sq_cm: 180.0,
    expected_status: "Failed",
    issue: "Non-standard unit symbol 'Gms.' instead of 'g'; missing '₹' symbol on MRP"
  },
  {
    id: "bourbon_biscuits",
    name: "Britannia Bourbon Biscuits",
    brand: "Britannia",
    company: "Britannia Industries Limited",
    category: "Biscuits & Bakery",
    pdp_area_sq_cm: 150.0,
    expected_status: "Failed",
    issue: "Non-standard unit 'gm'; missing 'inclusive of all taxes' clause on MRP"
  },
  {
    id: "amul_butter",
    name: "Amul Pasteurised Butter 500g",
    brand: "Amul",
    company: "Gujarat Co-operative Milk Marketing Federation Ltd. (Amul)",
    category: "Dairy Products",
    pdp_area_sq_cm: 140.0,
    expected_status: "Passed",
    issue: "Fully compliant statutory declarations"
  },
  {
    id: "aashirvaad_atta",
    name: "Aashirvaad Shudh Chakki Atta 5kg",
    brand: "Aashirvaad",
    company: "ITC Limited (Foods Division)",
    category: "Flours & Staples",
    pdp_area_sq_cm: 650.0,
    expected_status: "Failed",
    issue: "Unit symbol pluralized as 'Gms.'; required USP not clearly visible"
  },
  {
    id: "maggi_noodles",
    name: "Maggi 2-Minute Masala Noodles",
    brand: "Maggi",
    company: "Nestlé India Limited",
    category: "Instant Foods",
    pdp_area_sq_cm: 210.0,
    expected_status: "Passed",
    issue: "Statutory declarations compliant under Rule 6"
  },
  {
    id: "parle_g",
    name: "Parle-G Original Gluco Biscuits",
    brand: "Parle",
    company: "Parle Products Private Limited",
    category: "Biscuits & Bakery",
    pdp_area_sq_cm: 120.0,
    expected_status: "Passed",
    issue: "Fully compliant"
  },
  {
    id: "tata_salt",
    name: "Tata Salt Vacuum Evaporated 1kg",
    brand: "Tata Salt",
    company: "Tata Consumer Products Limited",
    category: "Salt & Spices",
    pdp_area_sq_cm: 320.0,
    expected_status: "Passed",
    issue: "Fully compliant declarations and SI unit 'kg'"
  },
  {
    id: "haldirams_bhujia",
    name: "Haldiram's Nagpur Aloo Bhujia",
    brand: "Haldiram's",
    company: "Haldiram Snacks Private Limited",
    category: "Traditional Namkeen",
    pdp_area_sq_cm: 190.0,
    expected_status: "Failed",
    issue: "Font height of net quantity numeral smaller than statutory minimum"
  },
  {
    id: "dabur_honey",
    name: "Dabur 100% Pure Honey 500g",
    brand: "Dabur",
    company: "Dabur India Limited",
    category: "Honey & Health Foods",
    pdp_area_sq_cm: 160.0,
    expected_status: "Failed",
    issue: "Missing grievance email in consumer care declaration"
  },
  {
    id: "saffola_gold",
    name: "Saffola Gold Pro Healthy Living Oil 1L",
    brand: "Saffola",
    company: "Marico Limited",
    category: "Edible Oils",
    pdp_area_sq_cm: 450.0,
    expected_status: "Passed",
    issue: "Compliant volume declaration '1 L' and complete packer details"
  }
];

const rulesEngine = new LegalMetrologyRulesEngine(companiesData as any);

class DatabaseStore {
  private scans: ProductScan[] = [];
  private nextId = 15;

  constructor() {
    this.seedBenchmarkData();
  }

  public seedBenchmarkData(): void {
    this.scans = [];
    this.nextId = 15;

    const benchmarkConfigs = [
      {
        id: 14,
        display_id: "#14",
        scan_id: "NYAYA-2026-0014",
        product_name: "Kurkure Schezwan Crispy Snack",
        brand_name: "Kurkure",
        company_name: "PepsiCo India Holdings Pvt. Ltd.",
        image_filename: "kurkure_schezwan_sample.jpg",
        pdp_area_sq_cm: 180.0,
        extracted: {
          commodity_name: "Kurkure Schezwan Crispy Snack",
          brand_name: "Kurkure",
          manufacturer_name_and_address: "PepsiCo India Holdings Pvt. Ltd., Sector 62, Gurugram - 122101, Haryana",
          net_quantity: "85 Gms.", // Non-compliant
          date_of_manufacture: "09/2026",
          best_before_expiry: "Best Before 4 Months",
          mrp: "MRP 20.00", // Missing ₹ and missing incl taxes
          unit_sale_price: "₹ 0.24 / g",
          consumer_care: "PepsiCo Helpline: 1800-22-4020, consumer.feedback@pepsico.com",
          detected_font_height_mm: 1.6,
          contrast_ratio: 4.1
        },
        officer_notes: "Statutory violation notice issued for non-standard unit 'Gms.' and missing tax inclusion clause on MRP."
      },
      {
        id: 13,
        display_id: "#13",
        scan_id: "NYAYA-2026-0013",
        product_name: "Britannia Bourbon Biscuits",
        brand_name: "Britannia",
        company_name: "Britannia Industries Limited",
        image_filename: "bourbon_biscuits_mismatch.jpg",
        pdp_area_sq_cm: 150.0,
        extracted: {
          commodity_name: "Bourbon Chocolate Flavoured Sandwich Biscuits",
          brand_name: "Britannia",
          manufacturer_name_and_address: "Britannia Industries Limited, 5/1A Hungerford Street, Kolkata - 700017, West Bengal",
          net_quantity: "150 gm", // Non-compliant
          date_of_manufacture: "08/2026",
          best_before_expiry: "Best Before 6 Months",
          mrp: "MRP ₹ 35.00", // Missing taxes clause
          unit_sale_price: "₹ 23.33 / 100 g",
          consumer_care: "1800-425-4449, feedback@britindia.com",
          detected_font_height_mm: 1.8,
          contrast_ratio: 4.8
        },
        officer_notes: "Non-standard unit symbol 'gm' used. Rule 12 requires 'g'."
      },
      {
        id: 12,
        display_id: "#12",
        scan_id: "NYAYA-2026-0012",
        product_name: "Amul Pasteurised Butter 500g",
        brand_name: "Amul",
        company_name: "Gujarat Co-operative Milk Marketing Federation Ltd. (Amul)",
        image_filename: "amul_butter_label.jpg",
        pdp_area_sq_cm: 140.0,
        extracted: {
          commodity_name: "Pasteurised Butter",
          brand_name: "Amul",
          manufacturer_name_and_address: "Gujarat Co-operative Milk Marketing Federation Ltd., Amul Dairy Road, Anand - 388001, Gujarat",
          net_quantity: "500 g",
          date_of_manufacture: "09/2026",
          best_before_expiry: "Use by 12 months",
          mrp: "MRP ₹ 275.00 (incl. of all taxes)",
          unit_sale_price: "₹ 55.00 / 100 g",
          consumer_care: "1800-258-3333, customercare@amul.coop",
          detected_font_height_mm: 2.8,
          contrast_ratio: 6.1
        },
        officer_notes: "Full statutory compliance verified under Rule 6."
      },
      {
        id: 11,
        display_id: "#11",
        scan_id: "NYAYA-2026-0011",
        product_name: "Aashirvaad Shudh Chakki Atta 5kg",
        brand_name: "Aashirvaad",
        company_name: "ITC Limited (Foods Division)",
        image_filename: "aashirvaad_atta_sample.jpg",
        pdp_area_sq_cm: 650.0,
        extracted: {
          commodity_name: "Whole Wheat Shudh Chakki Atta",
          brand_name: "Aashirvaad",
          manufacturer_name_and_address: "ITC Limited, Virginia House, 37 J.L. Nehru Road, Kolkata - 700071, West Bengal",
          net_quantity: "5000 Gms.", // Non-compliant unit
          date_of_manufacture: "08/2026",
          best_before_expiry: "Best Before 4 Months",
          mrp: "MRP ₹ 245.00 incl. of all taxes",
          unit_sale_price: "₹ 49.00 / kg",
          consumer_care: "1800-425-44444, itccares@itc.in",
          detected_font_height_mm: 2.1,
          contrast_ratio: 5.2
        },
        officer_notes: "Illegal pluralized unit symbol 'Gms.' detected."
      },
      {
        id: 10,
        display_id: "#10",
        scan_id: "NYAYA-2026-0010",
        product_name: "Maggi 2-Minute Masala Noodles",
        brand_name: "Maggi",
        company_name: "Nestlé India Limited",
        image_filename: "maggi_noodles_sample.jpg",
        pdp_area_sq_cm: 210.0,
        extracted: {
          commodity_name: "Instant Noodles with Tastemaker",
          brand_name: "Maggi",
          manufacturer_name_and_address: "Nestlé India Limited, 100/101 World Trade Centre, Barakhamba Lane, New Delhi - 110001",
          net_quantity: "280 g",
          date_of_manufacture: "07/2026",
          best_before_expiry: "Best Before 9 Months",
          mrp: "MRP ₹ 60.00 incl. of all taxes",
          unit_sale_price: "₹ 21.43 / 100 g",
          consumer_care: "1800-103-1947, wecare@in.nestle.com",
          detected_font_height_mm: 2.6,
          contrast_ratio: 5.8
        },
        officer_notes: "Statutory declarations verified under Legal Metrology Rules."
      },
      {
        id: 9,
        display_id: "#9",
        scan_id: "NYAYA-2026-0009",
        product_name: "Parle-G Original Gluco Biscuits",
        brand_name: "Parle",
        company_name: "Parle Products Private Limited",
        image_filename: "parle_g_sample.jpg",
        pdp_area_sq_cm: 120.0,
        extracted: {
          commodity_name: "Glucose Biscuits",
          brand_name: "Parle",
          manufacturer_name_and_address: "Parle Products Private Limited, North Level Crossing, Vile Parle East, Mumbai - 400057, Maharashtra",
          net_quantity: "250 g",
          date_of_manufacture: "08/2026",
          best_before_expiry: "Best Before 6 Months",
          mrp: "MRP ₹ 25.00 incl. of all taxes",
          unit_sale_price: "₹ 10.00 / 100 g",
          consumer_care: "1800-22-3450, cs@parle.biz",
          detected_font_height_mm: 2.5,
          contrast_ratio: 5.5
        },
        officer_notes: "Compliant packaging."
      },
      {
        id: 8,
        display_id: "#8",
        scan_id: "NYAYA-2026-0008",
        product_name: "Tata Salt Vacuum Evaporated",
        brand_name: "Tata Salt",
        company_name: "Tata Consumer Products Limited",
        image_filename: "tata_salt_sample.jpg",
        pdp_area_sq_cm: 320.0,
        extracted: {
          commodity_name: "Vacuum Evaporated Iodised Salt",
          brand_name: "Tata Salt",
          manufacturer_name_and_address: "Tata Consumer Products Limited, 1 Bishop Lefroy Road, Kolkata - 700020, West Bengal",
          net_quantity: "1 kg",
          date_of_manufacture: "08/2026",
          best_before_expiry: "Best Before 24 Months",
          mrp: "MRP ₹ 28.00 incl. of all taxes",
          unit_sale_price: "₹ 28.00 / kg",
          consumer_care: "1800-108-4488, care@tataconsumer.com",
          detected_font_height_mm: 4.2,
          contrast_ratio: 6.5
        },
        officer_notes: "Clear declarations and high font height compliance."
      },
      {
        id: 7,
        display_id: "#7",
        scan_id: "NYAYA-2026-0007",
        product_name: "Haldiram's Nagpur Aloo Bhujia",
        brand_name: "Haldiram's",
        company_name: "Haldiram Snacks Private Limited",
        image_filename: "haldirams_bhujia_sample.jpg",
        pdp_area_sq_cm: 190.0,
        extracted: {
          commodity_name: "Spicy Potato Noodles (Aloo Bhujia)",
          brand_name: "Haldiram's",
          manufacturer_name_and_address: "Haldiram Snacks Private Limited, B-1/H-8, Mohan Co-operative Industrial Estate, Mathura Road, New Delhi - 110044",
          net_quantity: "200 g",
          date_of_manufacture: "07/2026",
          best_before_expiry: "Best Before 5 Months",
          mrp: "MRP ₹ 55.00 incl. of all taxes",
          unit_sale_price: "₹ 27.50 / 100 g",
          consumer_care: "1800-102-7576, care@haldirams.com",
          detected_font_height_mm: 1.2, // Too small for PDP > 100cm2
          contrast_ratio: 5.0
        },
        officer_notes: "Numeral height 1.2mm violates Rule 7 (minimum 2.5mm required)."
      },
      {
        id: 6,
        display_id: "#6",
        scan_id: "NYAYA-2026-0006",
        product_name: "Dabur 100% Pure Honey",
        brand_name: "Dabur",
        company_name: "Dabur India Limited",
        image_filename: "dabur_honey_sample.jpg",
        pdp_area_sq_cm: 160.0,
        extracted: {
          commodity_name: "Pure Honey",
          brand_name: "Dabur",
          manufacturer_name_and_address: "Dabur India Limited, 8/3 Asaf Ali Road, New Delhi - 110002",
          net_quantity: "500 g",
          date_of_manufacture: "06/2026",
          best_before_expiry: "Best Before 18 Months",
          mrp: "MRP ₹ 220.00 incl. of all taxes",
          unit_sale_price: "₹ 44.00 / 100 g",
          consumer_care: "1800-103-1644", // Missing email address
          detected_font_height_mm: 2.5,
          contrast_ratio: 2.8 // Low contrast
        },
        officer_notes: "Rule 9 low contrast and missing consumer grievance email."
      },
      {
        id: 5,
        display_id: "#5",
        scan_id: "NYAYA-2026-0005",
        product_name: "Saffola Gold Pro Healthy Living Oil",
        brand_name: "Saffola",
        company_name: "Marico Limited",
        image_filename: "saffola_oil_sample.jpg",
        pdp_area_sq_cm: 450.0,
        extracted: {
          commodity_name: "Blended Edible Vegetable Oil",
          brand_name: "Saffola",
          manufacturer_name_and_address: "Marico Limited, 7th Floor Grande Palladium, 175 CST Road, Kalina, Santacruz East, Mumbai - 400098",
          net_quantity: "1 L",
          date_of_manufacture: "08/2026",
          best_before_expiry: "Best Before 9 Months",
          mrp: "MRP ₹ 185.00 incl. of all taxes",
          unit_sale_price: "₹ 185.00 / L",
          consumer_care: "1800-22-2248, csc@marico.com",
          detected_font_height_mm: 4.1,
          contrast_ratio: 6.2
        },
        officer_notes: "Fully compliant edible oil packaging."
      },
      {
        id: 4,
        display_id: "#4",
        scan_id: "NYAYA-2026-0004",
        product_name: "Bikaji Bikaneri Bhujia",
        brand_name: "Bikaji",
        company_name: "Bikaji Foods International Limited",
        image_filename: "bikaji_bhujia_sample.jpg",
        pdp_area_sq_cm: 190.0,
        extracted: {
          commodity_name: "Bikaneri Bhujia",
          brand_name: "Bikaji",
          manufacturer_name_and_address: "Bikaji Foods International Limited, F 196-199 Bichhwal Industrial Area, Bikaner - 334006, Rajasthan",
          net_quantity: "400 gms", // Non-compliant
          date_of_manufacture: "08/2026",
          best_before_expiry: "Best Before 6 Months",
          mrp: "MRP ₹ 110.00 incl. of all taxes",
          unit_sale_price: "₹ 27.50 / 100 g",
          consumer_care: "1800-203-4554, customercare@bikaji.com",
          detected_font_height_mm: 2.6,
          contrast_ratio: 5.3
        },
        officer_notes: "Non-standard unit symbol 'gms' used."
      },
      {
        id: 3,
        display_id: "#3",
        scan_id: "NYAYA-2026-0003",
        product_name: "Fortune Sunlite Refined Sunflower Oil",
        brand_name: "Fortune",
        company_name: "Adani Wilmar Limited",
        image_filename: "fortune_sunflower_sample.jpg",
        pdp_area_sq_cm: 420.0,
        extracted: {
          commodity_name: "Refined Sunflower Oil",
          brand_name: "Fortune",
          manufacturer_name_and_address: "Adani Wilmar Limited, Fortune House, Near Navrangpura Railway Crossing, Ahmedabad - 380009, Gujarat",
          net_quantity: "1 L",
          date_of_manufacture: "09/2026",
          best_before_expiry: "Best Before 9 Months",
          mrp: "MRP ₹ 145.00 incl. of all taxes",
          unit_sale_price: "₹ 145.00 / L",
          consumer_care: "1800-233-9999, customercare@adaniwilmar.in",
          detected_font_height_mm: 4.0,
          contrast_ratio: 5.9
        },
        officer_notes: "Fully compliant edible oil pouch."
      },
      {
        id: 2,
        display_id: "#2",
        scan_id: "NYAYA-2026-0002",
        product_name: "Patanjali Cow Ghee",
        brand_name: "Patanjali",
        company_name: "Patanjali Foods Limited",
        image_filename: "patanjali_ghee_sample.jpg",
        pdp_area_sq_cm: 220.0,
        extracted: {
          commodity_name: "Desi Cow Ghee",
          brand_name: "Patanjali",
          manufacturer_name_and_address: "Patanjali Foods Limited, Vill. Padartha, Laksar Road, Haridwar - 249404, Uttarakhand",
          net_quantity: "1 Ltr", // Non-compliant unit
          date_of_manufacture: "07/2026",
          best_before_expiry: "Best Before 9 Months",
          mrp: "MRP ₹ 650.00", // Missing taxes clause
          unit_sale_price: "₹ 650.00 / L",
          consumer_care: "1800-180-4187, feedback@patanjalifoods.com",
          detected_font_height_mm: 2.8,
          contrast_ratio: 5.1
        },
        officer_notes: "Non-standard unit 'Ltr' and missing tax clause."
      },
      {
        id: 1,
        display_id: "#1",
        scan_id: "NYAYA-2026-0001",
        product_name: "Good Day Cashew Cookies",
        brand_name: "Britannia",
        company_name: "Britannia Industries Limited",
        image_filename: "good_day_cashew_sample.jpg",
        pdp_area_sq_cm: 130.0,
        extracted: {
          commodity_name: "Cashew Cookies",
          brand_name: "Britannia",
          manufacturer_name_and_address: "Britannia Industries Limited, 5/1A Hungerford Street, Kolkata - 700017, West Bengal",
          net_quantity: "100 gms", // Non-compliant unit
          date_of_manufacture: "08/2026",
          best_before_expiry: "Best Before 6 Months",
          mrp: "MRP ₹ 30.00 incl. of all taxes",
          unit_sale_price: "₹ 30.00 / 100 g",
          consumer_care: "1800-425-4449, feedback@britindia.com",
          detected_font_height_mm: 2.4,
          contrast_ratio: 5.7
        },
        officer_notes: "Non-standard unit 'gms'."
      }
    ];

    const baseDate = new Date("2026-09-12T10:00:00.000Z");

    for (let i = 0; i < benchmarkConfigs.length; i++) {
      const cfg = benchmarkConfigs[i];
      const itemDate = new Date(baseDate.getTime() - i * 3600 * 1000 * 4);
      const evalRes = rulesEngine.evaluateCompliance(cfg.extracted, cfg.pdp_area_sq_cm);

      const h = itemDate.getHours();
      const h12 = h % 12 || 12;
      const ampm = h >= 12 ? "pm" : "am";
      const mStr = String(itemDate.getMinutes()).padStart(2, "0");
      const sStr = String(itemDate.getSeconds()).padStart(2, "0");
      const formattedTs = `${itemDate.getMonth() + 1}/${itemDate.getDate()}/${itemDate.getFullYear()}, ${h12}:${mStr}:${sStr} ${ampm}`;

      const scan: ProductScan = {
        id: cfg.id,
        display_id: cfg.display_id,
        scan_id: cfg.scan_id,
        product: cfg.product_name,
        product_name: cfg.product_name,
        brand_name: cfg.brand_name,
        company_name: cfg.company_name,
        image_filename: cfg.image_filename,
        image_url: cfg.image_filename ? `/uploads/${cfg.image_filename}` : undefined,
        image_path: cfg.image_filename ? `uploads/${cfg.image_filename}` : undefined,
        is_packaged_product: true,
        object_category: "PACKAGED_FOOD_COMMODITY",
        missing_count: evalRes.missing_count || 0,
        non_compliant_count: evalRes.non_compliant_count || 0,
        pdp_area_sq_cm: cfg.pdp_area_sq_cm,
        status: evalRes.status,
        overall_status: evalRes.status,
        risk_score: evalRes.risk_score.toFixed(2),
        compliance_score: evalRes.compliance_score,
        violations_count: evalRes.violations.length,
        extracted_data: cfg.extracted,
        evaluation_result: evalRes,
        officer_notes: cfg.officer_notes,
        inspector_id: "LMO-DL-7729",
        timestamp: formattedTs,
        created_at: itemDate.toISOString()
      };

      this.scans.push(scan);
    }
  }

  public getAllScans(): ProductScan[] {
    return [...this.scans].sort((a, b) => b.id - a.id);
  }

  public getScanById(idOrScanId: string): ProductScan | undefined {
    const numericId = parseInt(idOrScanId.replace("#", ""), 10);
    return this.scans.find(s => s.scan_id === idOrScanId || (!isNaN(numericId) && s.id === numericId));
  }

  public addScan(scan: Omit<ProductScan, "id" | "display_id">): ProductScan {
    const id = this.nextId++;
    const fullScan: ProductScan = {
      ...scan,
      id,
      display_id: `#${id}`
    };
    this.scans.unshift(fullScan);
    return fullScan;
  }

  public getDashboardStats(): Record<string, any> {
    const total = this.scans.length;
    const passed = this.scans.filter(s => s.status === "Passed" || s.overall_status === "Passed").length;
    const failed = this.scans.filter(s => s.status === "Failed" || s.overall_status === "Failed").length;
    const review = this.scans.filter(s => s.status === "Review Required" || s.overall_status === "Review Required").length;

    const avgCompliance = total > 0 ? Math.round(this.scans.reduce((acc, s) => acc + s.compliance_score, 0) / total) : 0;
    const highRiskCount = this.scans.filter(s => parseFloat(s.risk_score) >= 0.70).length;

    return {
      kpis: {
        total_scans: total,
        passed,
        failed,
        review_required: review,
        avg_compliance_score: avgCompliance,
        high_risk_scans: highRiskCount
      },
      recent_scans: this.getAllScans().slice(0, 5),
      top_violations: [
        { rule: "Rule 6(1)(c)", label: "Non-standard Metric Units ('gm', 'gms')", count: 6 },
        { rule: "Rule 6(1)(e)", label: "Missing 'incl. of all taxes' / currency symbol", count: 4 },
        { rule: "Rule 7 & 8", label: "Numeral Height below statutory minimum", count: 2 },
        { rule: "Rule 6(1)(f)", label: "Incomplete Consumer Care Details", count: 2 },
        { rule: "Rule 9", label: "Low Contrast / Readability Ratio", count: 1 }
      ]
    };
  }
}

export const dbStore = new DatabaseStore();
