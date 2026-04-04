"""
AgriIQ — Complete Synthetic Dataset Generator
Generates realistic Zimbabwe agricultural data for all 17 modules
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import json
import os

np.random.seed(42)
random.seed(42)

# ── Constants ─────────────────────────────────────────────────────────────────

FARMS = [
    {"id": "F001", "name": "Mazowe Valley Farm",     "province": "Mashonaland Central", "lat": -17.28, "lon": 30.97, "size_ha": 850,  "owner": "Tendai Moyo",      "type": "Commercial"},
    {"id": "F002", "name": "Chinhoyi Estates",        "province": "Mashonaland West",   "lat": -17.36, "lon": 30.19, "size_ha": 1200, "owner": "David Chikwanda",  "type": "Commercial"},
    {"id": "F003", "name": "Hippo Valley Block 3",    "province": "Masvingo",           "lat": -21.02, "lon": 31.78, "size_ha": 2100, "owner": "Hippo Valley Ltd", "type": "Corporate"},
    {"id": "F004", "name": "Mvurwi Mixed Farm",       "province": "Mashonaland Central","lat": -17.02, "lon": 30.86, "size_ha": 430,  "owner": "Grace Zimba",      "type": "Commercial"},
    {"id": "F005", "name": "Centenary Tobacco Estate","province": "Mashonaland Central","lat": -16.73, "lon": 31.11, "size_ha": 680,  "owner": "Farai Ncube",      "type": "Commercial"},
    {"id": "F006", "name": "Karoi Maize Cooperative", "province": "Mashonaland West",   "lat": -16.81, "lon": 29.68, "size_ha": 520,  "owner": "Karoi Coop Ltd",   "type": "Cooperative"},
    {"id": "F007", "name": "Chiredzi Sugar Block",    "province": "Masvingo",           "lat": -21.05, "lon": 31.67, "size_ha": 1800, "owner": "Triangle Ltd",     "type": "Corporate"},
    {"id": "F008", "name": "Mutoko Horticultural",    "province": "Mashonaland East",   "lat": -17.40, "lon": 32.22, "size_ha": 190,  "owner": "Spiwe Dube",       "type": "Smallholder"},
    {"id": "F009", "name": "Gweru Wheat Station",     "province": "Midlands",           "lat": -19.45, "lon": 29.81, "size_ha": 740,  "owner": "AgriCore Pvt Ltd", "type": "Commercial"},
    {"id": "F010", "name": "Bindura Soya Farm",       "province": "Mashonaland Central","lat": -17.30, "lon": 31.33, "size_ha": 560,  "owner": "Rudo Maposa",      "type": "Commercial"},
    {"id": "F011", "name": "Headlands Cotton Block",  "province": "Mashonaland East",   "lat": -18.27, "lon": 32.18, "size_ha": 380,  "owner": "Cotton Growers Co","type": "Cooperative"},
    {"id": "F012", "name": "Banket Mixed Estate",     "province": "Mashonaland West",   "lat": -17.39, "lon": 30.40, "size_ha": 620,  "owner": "Percy Hove",       "type": "Commercial"},
]

CROPS = ["Maize", "Tobacco", "Wheat", "Soya Bean", "Cotton", "Sugar Cane", "Horticulture", "Sunflower"]

CROP_CONFIG = {
    "Maize":       {"season": "Summer", "price_per_ton": 285,  "yield_range": (3.5, 7.2),  "color": "#f59e0b"},
    "Tobacco":     {"season": "Summer", "price_per_ton": 3200, "yield_range": (1.2, 2.8),  "color": "#8b5cf6"},
    "Wheat":       {"season": "Winter", "price_per_ton": 420,  "yield_range": (2.8, 5.5),  "color": "#d97706"},
    "Soya Bean":   {"season": "Summer", "price_per_ton": 560,  "yield_range": (1.5, 3.2),  "color": "#10b981"},
    "Cotton":      {"season": "Summer", "price_per_ton": 680,  "yield_range": (0.8, 2.1),  "color": "#f3f4f6"},
    "Sugar Cane":  {"season": "Annual", "price_per_ton": 48,   "yield_range": (65, 110),   "color": "#6ee7b7"},
    "Horticulture":{"season": "Annual", "price_per_ton": 1200, "yield_range": (8.0, 22.0), "color": "#f472b6"},
    "Sunflower":   {"season": "Summer", "price_per_ton": 380,  "yield_range": (0.9, 1.8),  "color": "#fbbf24"},
}

PROVINCES = list(set(f["province"] for f in FARMS))

SUPPLIERS = [
    {"id": "S001", "name": "Seed Co Zimbabwe",       "category": "Seeds",      "contact": "0242-481111"},
    {"id": "S002", "name": "Quton Seeds",             "category": "Seeds",      "contact": "0242-336120"},
    {"id": "S003", "name": "ZimPhos",                 "category": "Fertilizer", "contact": "0292-221144"},
    {"id": "S004", "name": "Windmill Zimbabwe",       "category": "Fertilizer", "contact": "0242-664141"},
    {"id": "S005", "name": "Agrico",                  "category": "Chemicals",  "contact": "0242-703921"},
    {"id": "S006", "name": "Farm & City Centre",      "category": "Equipment",  "contact": "0242-759401"},
    {"id": "S007", "name": "Meikles Agri",            "category": "Chemicals",  "contact": "0242-252061"},
    {"id": "S008", "name": "John Deere Zimbabwe",     "category": "Equipment",  "contact": "0242-667891"},
]

MARKETS = [
    "Grain Marketing Board (GMB)",
    "TIMB Auction Floor",
    "COTTCO Ginnery",
    "Harare Fresh Produce Market",
    "Export — EU Markets",
    "Export — South Africa",
    "Private Processors",
    "Milling Companies",
]

# ── Helper Functions ───────────────────────────────────────────────────────────

def date_range(start, end, freq="D"):
    return pd.date_range(start=start, end=end, freq=freq)

def rand_between(lo, hi, size=1):
    return np.random.uniform(lo, hi, size)

# ── 1. Farm Master Table ───────────────────────────────────────────────────────

def gen_farms():
    records = []
    for f in FARMS:
        primary_crop = random.choice(CROPS)
        cfg = CROP_CONFIG[primary_crop]
        yield_ha = round(rand_between(*cfg["yield_range"])[0], 2)
        revenue = round(yield_ha * f["size_ha"] * cfg["price_per_ton"] * random.uniform(0.7, 0.95), 2)
        cost = round(revenue * random.uniform(0.45, 0.68), 2)
        records.append({
            **f,
            "primary_crop": primary_crop,
            "secondary_crop": random.choice([c for c in CROPS if c != primary_crop]),
            "irrigation_type": random.choice(["Centre Pivot", "Drip", "Flood", "Rain-fed", "Sprinkler"]),
            "yield_tons_ha": yield_ha,
            "revenue_usd": revenue,
            "cost_usd": cost,
            "profit_usd": round(revenue - cost, 2),
            "profit_margin_pct": round((revenue - cost) / revenue * 100, 1),
            "workers_permanent": random.randint(15, 120),
            "workers_seasonal": random.randint(40, 350),
            "harvest_date": (datetime(2026, 3, 1) + timedelta(days=random.randint(0, 90))).strftime("%Y-%m-%d"),
            "status": random.choice(["Active", "Active", "Active", "Harvest Phase", "Off-Season"]),
            "certification": random.choice(["GlobalGAP", "Organic", "None", "HACCP", "None"]),
            "water_source": random.choice(["Borehole", "River", "Dam", "Irrigation Scheme"]),
        })
    return pd.DataFrame(records)

# ── 2. Monthly Performance (24 months) ────────────────────────────────────────

def gen_monthly_performance():
    records = []
    for f in FARMS:
        for month_offset in range(24):
            dt = datetime(2024, 4, 1) + timedelta(days=30 * month_offset)
            base_rev = random.uniform(18000, 280000)
            seasonal_factor = 1.3 if dt.month in [3, 4, 9, 10] else 0.85
            revenue = round(base_rev * seasonal_factor, 2)
            cost = round(revenue * random.uniform(0.42, 0.70), 2)
            records.append({
                "farm_id": f["id"],
                "farm_name": f["name"],
                "province": f["province"],
                "month": dt.strftime("%Y-%m"),
                "month_label": dt.strftime("%b %Y"),
                "revenue_usd": revenue,
                "cost_usd": cost,
                "profit_usd": round(revenue - cost, 2),
                "profit_margin_pct": round((revenue - cost) / revenue * 100, 1),
                "yield_tons": round(random.uniform(20, 850), 1),
                "yield_per_ha": round(random.uniform(1.2, 8.5), 2),
            })
    return pd.DataFrame(records)

# ── 3. P&L Detail ─────────────────────────────────────────────────────────────

def gen_pnl():
    records = []
    for f in FARMS:
        for season in ["2024 Summer", "2024 Winter", "2025 Summer"]:
            revenue = round(random.uniform(35000, 480000), 2)
            seeds = round(revenue * random.uniform(0.06, 0.11), 2)
            fertilizer = round(revenue * random.uniform(0.09, 0.16), 2)
            labour = round(revenue * random.uniform(0.10, 0.18), 2)
            irrigation = round(revenue * random.uniform(0.03, 0.08), 2)
            equipment = round(revenue * random.uniform(0.04, 0.09), 2)
            transport = round(revenue * random.uniform(0.03, 0.07), 2)
            chemicals = round(revenue * random.uniform(0.02, 0.06), 2)
            storage = round(revenue * random.uniform(0.01, 0.04), 2)
            total_cost = seeds + fertilizer + labour + irrigation + equipment + transport + chemicals + storage
            records.append({
                "farm_id": f["id"],
                "farm_name": f["name"],
                "province": f["province"],
                "season": season,
                "revenue_usd": revenue,
                "seeds_usd": seeds,
                "fertilizer_usd": fertilizer,
                "labour_usd": labour,
                "irrigation_usd": irrigation,
                "equipment_usd": equipment,
                "transport_usd": transport,
                "chemicals_usd": chemicals,
                "storage_usd": storage,
                "total_cost_usd": round(total_cost, 2),
                "gross_profit_usd": round(revenue - total_cost, 2),
                "profit_margin_pct": round((revenue - total_cost) / revenue * 100, 1),
                "revenue_per_ha": round(revenue / f["size_ha"], 2),
                "profit_per_ha": round((revenue - total_cost) / f["size_ha"], 2),
            })
    return pd.DataFrame(records)

# ── 4. Inventory / Inputs ─────────────────────────────────────────────────────

def gen_inventory():
    items = [
        ("SC403 Maize Seed", "Seeds", "50kg bag", 45, 120, 20),
        ("SC719 Maize Seed", "Seeds", "50kg bag", 38, 100, 15),
        ("Quton 7235 Cotton Seed", "Seeds", "25kg bag", 12, 40, 8),
        ("SDS 5 Soya Seed", "Seeds", "50kg bag", 25, 60, 10),
        ("AN 34.5% Nitrogen", "Fertilizer", "50kg bag", 180, 400, 50),
        ("Compound D Basal", "Fertilizer", "50kg bag", 220, 500, 60),
        ("Ammonium Nitrate", "Fertilizer", "50kg bag", 160, 380, 45),
        ("Urea 46%", "Fertilizer", "50kg bag", 195, 420, 55),
        ("Dimethoate EC40", "Chemicals", "5L drum", 35, 80, 10),
        ("Cypermethrin 200EC", "Chemicals", "1L bottle", 60, 120, 15),
        ("Glyphosate 480", "Chemicals", "20L drum", 28, 65, 8),
        ("Mancozeb 80WP", "Chemicals", "5kg pack", 45, 100, 12),
        ("Tractor Parts Kit", "Equipment", "Set", 4, 12, 2),
        ("Irrigation Pipes 6\"", "Equipment", "100m roll", 8, 20, 3),
        ("Fuel — Diesel", "Fuel", "Litres", 2400, 5000, 500),
        ("Lubricating Oil", "Fuel", "20L drum", 18, 45, 5),
    ]
    records = []
    for farm in FARMS:
        for item_name, category, unit, curr, max_cap, reorder_pt in items:
            if random.random() < 0.75:
                qty = random.randint(max(1, curr - 10), max_cap)
                status = "Critical" if qty <= reorder_pt else ("Low" if qty <= reorder_pt * 1.5 else "OK")
                records.append({
                    "farm_id": farm["id"],
                    "farm_name": farm["name"],
                    "item_name": item_name,
                    "category": category,
                    "unit": unit,
                    "qty_current": qty,
                    "qty_max": max_cap,
                    "reorder_point": reorder_pt,
                    "status": status,
                    "last_restocked": (datetime(2026, 1, 1) + timedelta(days=random.randint(0, 80))).strftime("%Y-%m-%d"),
                    "supplier": random.choice([s["name"] for s in SUPPLIERS]),
                    "unit_cost_usd": round(random.uniform(2.5, 85.0), 2),
                })
    return pd.DataFrame(records)

# ── 5. Harvest Movement ───────────────────────────────────────────────────────

def gen_harvest_movement():
    movement_types = ["Sale to Market", "Storage Transfer", "Export Shipment", "Processing Intake", "Spoilage", "Cooperative Delivery"]
    records = []
    for farm in FARMS:
        for _ in range(random.randint(15, 35)):
            mv_date = datetime(2025, 7, 1) + timedelta(days=random.randint(0, 270))
            mv_type = random.choice(movement_types)
            crop = random.choice(CROPS)
            qty = round(random.uniform(5, 420), 1)
            price = CROP_CONFIG[crop]["price_per_ton"]
            records.append({
                "farm_id": farm["id"],
                "farm_name": farm["name"],
                "date": mv_date.strftime("%Y-%m-%d"),
                "movement_type": mv_type,
                "crop": crop,
                "quantity_tons": qty,
                "destination": random.choice(MARKETS),
                "value_usd": round(qty * price * random.uniform(0.88, 1.05), 2),
                "transport_mode": random.choice(["Road — Own Truck", "Road — 3PL", "Rail", "Direct Field"]),
                "status": random.choice(["Completed", "Completed", "In Transit", "Pending"]),
                "driver": f"Driver {random.randint(1,20):02d}",
                "distance_km": random.randint(15, 380),
            })
    return pd.DataFrame(records).sort_values("date").reset_index(drop=True)

# ── 6. Yield Forecasting Data ─────────────────────────────────────────────────

def gen_yield_forecast():
    records = []
    for farm in FARMS:
        crop = farm.get("primary_crop", "Maize") if "primary_crop" in farm else random.choice(CROPS)
        cfg = CROP_CONFIG[random.choice(CROPS)]
        for week_offset in range(-52, 14):
            date = datetime(2025, 4, 1) + timedelta(weeks=week_offset)
            base_yield = rand_between(*cfg["yield_range"])[0]
            rainfall = round(random.uniform(10, 180), 1)
            temp = round(random.uniform(18, 34), 1)
            humidity = round(random.uniform(40, 90), 1)
            if week_offset < 0:
                actual = round(base_yield * (1 + (rainfall - 80) / 800), 2)
                forecast = None
                confidence = None
            else:
                actual = None
                forecast = round(base_yield * (1 + (rainfall - 80) / 800) * random.uniform(0.92, 1.08), 2)
                confidence = round(random.uniform(72, 94), 1)
            records.append({
                "farm_id": farm["id"],
                "farm_name": farm["name"],
                "week": date.strftime("%Y-%W"),
                "date": date.strftime("%Y-%m-%d"),
                "actual_yield_tons_ha": actual,
                "forecast_yield_tons_ha": forecast,
                "confidence_pct": confidence,
                "rainfall_mm": rainfall,
                "temperature_c": temp,
                "humidity_pct": humidity,
                "soil_moisture": round(random.uniform(20, 80), 1),
                "pest_pressure": random.choice(["Low", "Low", "Medium", "Medium", "High"]),
                "disease_risk": random.choice(["Low", "Low", "Medium", "High"]),
            })
    return pd.DataFrame(records)

# ── 7. Reorder Optimizer ──────────────────────────────────────────────────────

def gen_reorder():
    records = []
    for farm in FARMS:
        for supplier in random.sample(SUPPLIERS, k=random.randint(3, 6)):
            days_to_plant = random.randint(-10, 90)
            supplier_lead = random.randint(5, 21)
            urgency = "CRITICAL" if days_to_plant < supplier_lead else ("HIGH" if days_to_plant < supplier_lead * 2 else "MEDIUM" if days_to_plant < 60 else "LOW")
            records.append({
                "farm_id": farm["id"],
                "farm_name": farm["name"],
                "supplier_name": supplier["name"],
                "category": supplier["category"],
                "item": f"{supplier['category']} — Standard Order",
                "qty_needed": random.randint(10, 200),
                "unit": "bags/drums",
                "estimated_cost_usd": round(random.uniform(800, 18000), 2),
                "days_to_planting": days_to_plant,
                "supplier_lead_days": supplier_lead,
                "urgency": urgency,
                "recommended_order_date": (datetime.today() + timedelta(days=max(0, days_to_plant - supplier_lead))).strftime("%Y-%m-%d"),
                "last_order_date": (datetime(2025, 10, 1) + timedelta(days=random.randint(0, 180))).strftime("%Y-%m-%d"),
            })
    return pd.DataFrame(records)

# ── 8. Supply Chain Pipeline ──────────────────────────────────────────────────

def gen_supply_chain():
    statuses = ["Field Harvest", "Transport", "Storage", "Processing", "Delivered", "Export Cleared"]
    records = []
    for i in range(180):
        farm = random.choice(FARMS)
        crop = random.choice(CROPS)
        qty = round(random.uniform(10, 600), 1)
        start = datetime(2025, 8, 1) + timedelta(days=random.randint(0, 240))
        stage = random.choice(statuses)
        records.append({
            "shipment_id": f"SHP-{i+1001}",
            "farm_id": farm["id"],
            "farm_name": farm["name"],
            "crop": crop,
            "quantity_tons": qty,
            "value_usd": round(qty * CROP_CONFIG[crop]["price_per_ton"], 2),
            "origin_province": farm["province"],
            "destination": random.choice(MARKETS),
            "current_stage": stage,
            "start_date": start.strftime("%Y-%m-%d"),
            "expected_delivery": (start + timedelta(days=random.randint(3, 21))).strftime("%Y-%m-%d"),
            "days_delayed": random.choice([0, 0, 0, 1, 2, 3, 5]),
            "transport_mode": random.choice(["Road", "Rail", "Road — Refrigerated"]),
            "storage_facility": random.choice(["Harare Grain Silo", "Bulawayo Cold Store", "Gweru Warehouse", "Farm Storage", "GMB Depot"]),
        })
    return pd.DataFrame(records)

# ── 9. Supplier Credit & Risk ─────────────────────────────────────────────────

def gen_supplier_credit():
    records = []
    for farm in FARMS:
        for supplier in SUPPLIERS:
            credit_limit = random.randint(5000, 80000)
            outstanding = round(credit_limit * random.uniform(0.1, 1.15), 2)
            overdue = round(outstanding * random.uniform(0, 0.4), 2)
            risk = "HIGH" if outstanding > credit_limit or overdue > 5000 else ("MEDIUM" if overdue > 1000 else "LOW")
            records.append({
                "farm_id": farm["id"],
                "farm_name": farm["name"],
                "supplier_id": supplier["id"],
                "supplier_name": supplier["name"],
                "category": supplier["category"],
                "credit_limit_usd": credit_limit,
                "outstanding_usd": outstanding,
                "overdue_usd": overdue,
                "credit_utilization_pct": round(outstanding / credit_limit * 100, 1),
                "risk_level": risk,
                "days_overdue": random.choice([0, 0, 0, 15, 30, 45, 60, 90]),
                "payment_terms_days": random.choice([30, 45, 60, 90]),
                "last_payment_date": (datetime(2026, 1, 1) + timedelta(days=random.randint(0, 80))).strftime("%Y-%m-%d"),
                "supply_status": "Suspended" if risk == "HIGH" and random.random() < 0.3 else "Active",
            })
    return pd.DataFrame(records)

# ── 10. Marketing ROI ─────────────────────────────────────────────────────────

def gen_marketing_roi():
    campaigns = [
        "GMB Partnership Drive", "EU Export Push Q1", "Tobacco Pre-Season Campaign",
        "Cooperative Member Drive", "Digital — LinkedIn AgriIQ", "Radio — ZBC Farm Show",
        "Trade Show — Zimbabwe Agrishow", "WhatsApp Farmer Network",
    ]
    records = []
    for camp in campaigns:
        for month_offset in range(12):
            dt = datetime(2025, 4, 1) + timedelta(days=30 * month_offset)
            spend = round(random.uniform(500, 12000), 2)
            revenue_lift = round(spend * random.uniform(1.2, 6.8), 2)
            records.append({
                "campaign": camp,
                "month": dt.strftime("%Y-%m"),
                "month_label": dt.strftime("%b %Y"),
                "spend_usd": spend,
                "revenue_lift_usd": revenue_lift,
                "roi_pct": round((revenue_lift - spend) / spend * 100, 1),
                "new_buyers": random.randint(0, 45),
                "impressions": random.randint(500, 85000),
                "channel": random.choice(["Digital", "Traditional Media", "Events", "Direct"]),
            })
    return pd.DataFrame(records)

# ── 11. Market Price Watch ────────────────────────────────────────────────────

def gen_market_prices():
    records = []
    for crop in CROPS:
        base_price = CROP_CONFIG[crop]["price_per_ton"]
        for day_offset in range(365):
            date = datetime(2025, 4, 1) + timedelta(days=day_offset)
            records.append({
                "date": date.strftime("%Y-%m-%d"),
                "crop": crop,
                "gmb_price": round(base_price * random.uniform(0.88, 1.08), 2),
                "timb_price": round(base_price * random.uniform(0.90, 1.12), 2) if crop == "Tobacco" else None,
                "cottco_price": round(base_price * random.uniform(0.85, 1.05), 2) if crop == "Cotton" else None,
                "private_buyer_price": round(base_price * random.uniform(0.92, 1.15), 2),
                "export_price_usd": round(base_price * random.uniform(1.05, 1.35), 2),
                "regional_sa_price": round(base_price * random.uniform(0.95, 1.20), 2),
                "recommended_channel": random.choice(["GMB", "Private Buyer", "Export", "TIMB", "COTTCO"]),
            })
    return pd.DataFrame(records)

# ── 12. Buyer Satisfaction ────────────────────────────────────────────────────

def gen_buyer_satisfaction():
    buyers = ["GMB Harare", "Cairns Foods", "National Foods", "Dairibord", "Delta Corp", "Export Broker EU", "Pick n Pay SA", "Innscor"]
    records = []
    for buyer in buyers:
        for month_offset in range(18):
            dt = datetime(2024, 10, 1) + timedelta(days=30 * month_offset)
            overall = round(random.uniform(3.0, 5.0), 1)
            records.append({
                "buyer": buyer,
                "month": dt.strftime("%Y-%m"),
                "month_label": dt.strftime("%b %Y"),
                "overall_score": overall,
                "quality_score": round(overall + random.uniform(-0.5, 0.5), 1),
                "delivery_score": round(overall + random.uniform(-0.7, 0.4), 1),
                "payment_score": round(random.uniform(3.5, 5.0), 1),
                "complaints": random.randint(0, 8),
                "repeat_orders": random.randint(1, 12),
                "volume_tons": round(random.uniform(50, 1800), 1),
                "revenue_usd": round(random.uniform(15000, 380000), 2),
            })
    return pd.DataFrame(records)

# ── 13. Labour Intelligence ───────────────────────────────────────────────────

def gen_labour():
    records = []
    for farm in FARMS:
        for month_offset in range(12):
            dt = datetime(2025, 4, 1) + timedelta(days=30 * month_offset)
            is_peak = dt.month in [11, 12, 1, 2, 3, 9, 10]
            perm = random.randint(15, 120)
            seasonal = random.randint(60, 350) if is_peak else random.randint(10, 80)
            records.append({
                "farm_id": farm["id"],
                "farm_name": farm["name"],
                "month": dt.strftime("%Y-%m"),
                "month_label": dt.strftime("%b %Y"),
                "permanent_workers": perm,
                "seasonal_workers": seasonal,
                "total_workers": perm + seasonal,
                "labour_cost_usd": round((perm * 220 + seasonal * 95) * random.uniform(0.9, 1.1), 2),
                "cost_per_ha": round(random.uniform(28, 95), 2),
                "overtime_hours": random.randint(0, 480) if is_peak else random.randint(0, 80),
                "vacancies": random.randint(0, 15),
                "turnover_pct": round(random.uniform(2, 18), 1),
                "training_completed": random.randint(0, 45),
                "productivity_score": round(random.uniform(65, 98), 1),
                "season_type": "Peak" if is_peak else "Off-Peak",
            })
    return pd.DataFrame(records)

# ── 14. Post-Harvest Loss ─────────────────────────────────────────────────────

def gen_losses():
    loss_causes = ["Storage Spoilage", "Pest Infestation", "Transport Damage", "Grading Downgrade", "Theft", "Processing Waste", "Weather Damage"]
    records = []
    for farm in FARMS:
        for season in ["2024 Summer", "2024 Winter", "2025 Summer"]:
            for cause in loss_causes:
                total_harvest = round(random.uniform(100, 2000), 1)
                loss_pct = round(random.uniform(0.5, 12.0), 2)
                loss_tons = round(total_harvest * loss_pct / 100, 2)
                crop = random.choice(CROPS)
                records.append({
                    "farm_id": farm["id"],
                    "farm_name": farm["name"],
                    "season": season,
                    "loss_cause": cause,
                    "crop": crop,
                    "total_harvest_tons": total_harvest,
                    "loss_tons": loss_tons,
                    "loss_pct": loss_pct,
                    "loss_value_usd": round(loss_tons * CROP_CONFIG[crop]["price_per_ton"], 2),
                    "recoverable": random.choice([True, False]),
                    "intervention": random.choice(["Cold storage upgrade", "Pest control applied", "None", "Packaging improved", "Security added"]),
                })
    return pd.DataFrame(records)

# ── 15. Agri-Economic Watch ───────────────────────────────────────────────────

def gen_economic_watch():
    records = []
    for day_offset in range(365):
        date = datetime(2025, 4, 1) + timedelta(days=day_offset)
        month = date.month
        # Rainy season Nov-Mar
        rainfall = round(random.uniform(80, 220) if month in [11, 12, 1, 2, 3] else random.uniform(5, 50), 1)
        records.append({
            "date": date.strftime("%Y-%m-%d"),
            "month": date.strftime("%Y-%m"),
            "rainfall_mm": rainfall,
            "temperature_c": round(random.uniform(16, 36), 1),
            "drought_index": round(max(0, 100 - rainfall * 0.6 + random.uniform(-10, 10)), 1),
            "fuel_price_usd_l": round(random.uniform(1.15, 1.55), 3),
            "fertilizer_index": round(random.uniform(85, 130), 1),
            "electricity_availability_pct": round(random.uniform(45, 90), 1),
            "usd_zwg_rate": round(random.uniform(13.5, 18.2), 2),
            "global_maize_usd_ton": round(random.uniform(195, 285), 2),
            "global_wheat_usd_ton": round(random.uniform(220, 310), 2),
            "global_soya_usd_ton": round(random.uniform(380, 520), 2),
            "el_nino_alert": rainfall < 30,
            "planting_window": date.month in [10, 11, 12],
        })
    return pd.DataFrame(records)

# ── 16. Board Reports Summary ─────────────────────────────────────────────────

def gen_board_summary(farms_df, pnl_df, losses_df):
    seasons = ["2024 Summer", "2024 Winter", "2025 Summer"]
    records = []
    for season in seasons:
        pnl_s = pnl_df[pnl_df["season"] == season]
        loss_s = losses_df[losses_df["season"] == season]
        records.append({
            "season": season,
            "total_revenue_usd": round(pnl_s["revenue_usd"].sum(), 2),
            "total_cost_usd": round(pnl_s["total_cost_usd"].sum(), 2),
            "total_profit_usd": round(pnl_s["gross_profit_usd"].sum(), 2),
            "avg_profit_margin_pct": round(pnl_s["profit_margin_pct"].mean(), 1),
            "total_loss_value_usd": round(loss_s["loss_value_usd"].sum(), 2),
            "farms_active": len(farms_df),
            "total_hectares": farms_df["size_ha"].sum(),
            "top_farm": pnl_s.groupby("farm_name")["gross_profit_usd"].sum().idxmax() if not pnl_s.empty else "N/A",
            "top_crop": random.choice(CROPS),
            "risk_alerts": random.randint(2, 8),
            "recommendations": "Increase cold storage capacity; review labour costs in peak season; explore EU export channels",
        })
    return pd.DataFrame(records)

# ── Weather Stations ──────────────────────────────────────────────────────────

def gen_weather():
    stations = [
        {"station": "Harare Airport",    "lat": -17.93, "lon": 31.09, "province": "Harare"},
        {"station": "Chinhoyi Met",      "lat": -17.36, "lon": 30.19, "province": "Mashonaland West"},
        {"station": "Masvingo Airport",  "lat": -20.05, "lon": 30.86, "province": "Masvingo"},
        {"station": "Gweru Airport",     "lat": -19.45, "lon": 29.86, "province": "Midlands"},
        {"station": "Mutare Airport",    "lat": -18.99, "lon": 32.63, "province": "Manicaland"},
        {"station": "Bindura Met",       "lat": -17.30, "lon": 31.33, "province": "Mashonaland Central"},
    ]
    records = []
    for st in stations:
        for day_offset in range(365):
            date = datetime(2025, 4, 1) + timedelta(days=day_offset)
            month = date.month
            is_rainy = month in [11, 12, 1, 2, 3]
            records.append({
                **st,
                "date": date.strftime("%Y-%m-%d"),
                "rainfall_mm": round(random.uniform(8, 180) if is_rainy else random.uniform(0, 25), 1),
                "max_temp_c": round(random.uniform(22, 38), 1),
                "min_temp_c": round(random.uniform(10, 22), 1),
                "humidity_pct": round(random.uniform(40, 92), 1),
                "wind_speed_kmh": round(random.uniform(5, 45), 1),
            })
    return pd.DataFrame(records)

# ── Main ──────────────────────────────────────────────────────────────────────

def generate_all():
    print("🌾 AgriIQ — Generating complete dataset...")
    os.makedirs("data/csv", exist_ok=True)

    farms_df = gen_farms()
    monthly_df = gen_monthly_performance()
    pnl_df = gen_pnl()
    inventory_df = gen_inventory()
    movement_df = gen_harvest_movement()
    forecast_df = gen_yield_forecast()
    reorder_df = gen_reorder()
    supply_chain_df = gen_supply_chain()
    supplier_credit_df = gen_supplier_credit()
    marketing_df = gen_marketing_roi()
    market_prices_df = gen_market_prices()
    buyer_sat_df = gen_buyer_satisfaction()
    labour_df = gen_labour()
    losses_df = gen_losses()
    economic_df = gen_economic_watch()
    board_df = gen_board_summary(farms_df, pnl_df, losses_df)
    weather_df = gen_weather()

    datasets = {
        "farms": farms_df,
        "monthly_performance": monthly_df,
        "pnl": pnl_df,
        "inventory": inventory_df,
        "harvest_movement": movement_df,
        "yield_forecast": forecast_df,
        "reorder_optimizer": reorder_df,
        "supply_chain": supply_chain_df,
        "supplier_credit": supplier_credit_df,
        "marketing_roi": marketing_df,
        "market_prices": market_prices_df,
        "buyer_satisfaction": buyer_sat_df,
        "labour": labour_df,
        "losses": losses_df,
        "economic_watch": economic_df,
        "board_summary": board_df,
        "weather": weather_df,
    }

    for name, df in datasets.items():
        path = f"data/csv/{name}.csv"
        df.to_csv(path, index=False)
        print(f"  ✅ {name}.csv — {len(df):,} rows")

    # Also save farm metadata as JSON for map
    farms_df.to_json("data/csv/farms.json", orient="records", indent=2)
    print(f"\n✅ All datasets generated successfully!")
    return datasets

if __name__ == "__main__":
    generate_all()
