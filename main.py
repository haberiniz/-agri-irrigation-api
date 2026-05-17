# main.py - Système Agricole Algérien Intelligent v3.0
# Avec météo réelle (Open-Meteo), 58 wilayas, 50+ cultures
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
import numpy as np
import httpx
import asyncio

app = FastAPI(title="🌾 Système Agricole Algérien Intelligent v3.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# 📍 58 WILAYAS D'ALGÉRIE (EN ORDRE OFFICIEL)
# ============================================================
WILAYA_COORDINATES = {
    1:  {"name": "Adrar",              "lat": 27.8667, "lon": -0.2833},
    2:  {"name": "Chlef",              "lat": 36.1650, "lon":  1.3317},
    3:  {"name": "Laghouat",           "lat": 33.8000, "lon":  2.8650},
    4:  {"name": "Oum El Bouaghi",     "lat": 35.8775, "lon":  7.1136},
    5:  {"name": "Batna",              "lat": 35.5667, "lon":  6.1667},
    6:  {"name": "Béjaïa",             "lat": 36.7500, "lon":  5.0833},
    7:  {"name": "Biskra",             "lat": 34.8500, "lon":  5.7300},
    8:  {"name": "Béchar",             "lat": 31.6167, "lon": -2.2167},
    9:  {"name": "Blida",              "lat": 36.4700, "lon":  2.8300},
    10: {"name": "Bouira",             "lat": 36.3800, "lon":  3.9000},
    11: {"name": "Tamanrasset",        "lat": 22.7850, "lon":  5.5228},
    12: {"name": "Tébessa",            "lat": 35.4000, "lon":  8.1167},
    13: {"name": "Tlemcen",            "lat": 34.8828, "lon": -1.3167},
    14: {"name": "Tiaret",             "lat": 35.3667, "lon":  1.3167},
    15: {"name": "Tizi Ouzou",         "lat": 36.7200, "lon":  4.0500},
    16: {"name": "Alger",              "lat": 36.7764, "lon":  3.0586},
    17: {"name": "Djelfa",             "lat": 34.6700, "lon":  3.2500},
    18: {"name": "Jijel",              "lat": 36.8167, "lon":  5.7667},
    19: {"name": "Sétif",              "lat": 36.1900, "lon":  5.4100},
    20: {"name": "Saïda",              "lat": 34.8300, "lon":  0.1500},
    21: {"name": "Skikda",             "lat": 36.8667, "lon":  6.9000},
    22: {"name": "Sidi Bel Abbès",     "lat": 35.1900, "lon": -0.6400},
    23: {"name": "Annaba",             "lat": 36.9000, "lon":  7.7667},
    24: {"name": "Guelma",             "lat": 36.4667, "lon":  7.4333},
    25: {"name": "Constantine",        "lat": 36.3650, "lon":  6.6147},
    26: {"name": "Médéa",              "lat": 36.2675, "lon":  2.7500},
    27: {"name": "Mostaganem",         "lat": 35.9300, "lon":  0.0900},
    28: {"name": "M'Sila",             "lat": 35.7058, "lon":  4.5419},
    29: {"name": "Mascara",            "lat": 35.4000, "lon":  0.1333},
    30: {"name": "Ouargla",            "lat": 31.9500, "lon":  5.3167},
    31: {"name": "Oran",               "lat": 35.6969, "lon": -0.6331},
    32: {"name": "El Bayadh",          "lat": 33.6833, "lon":  1.0167},
    33: {"name": "Illizi",             "lat": 26.5000, "lon":  8.4167},
    34: {"name": "Bordj Bou Arreridj", "lat": 36.0700, "lon":  4.7600},
    35: {"name": "Boumerdès",          "lat": 36.7600, "lon":  3.4800},
    36: {"name": "El Tarf",            "lat": 36.7667, "lon":  8.3167},
    37: {"name": "Tindouf",            "lat": 27.6667, "lon": -8.1333},
    38: {"name": "Tissemsilt",         "lat": 35.6000, "lon":  1.8167},
    39: {"name": "El Oued",            "lat": 33.3667, "lon":  6.8667},
    40: {"name": "Khenchela",          "lat": 35.4333, "lon":  7.1333},
    41: {"name": "Souk Ahras",         "lat": 36.2833, "lon":  7.9500},
    42: {"name": "Tipaza",             "lat": 36.5900, "lon":  2.4400},
    43: {"name": "Mila",               "lat": 36.4500, "lon":  6.2667},
    44: {"name": "Aïn Defla",          "lat": 36.2600, "lon":  1.9700},
    45: {"name": "Naâma",              "lat": 33.2667, "lon": -0.3167},
    46: {"name": "Aïn Témouchent",     "lat": 35.3000, "lon": -1.1333},
    47: {"name": "Ghardaïa",           "lat": 32.4833, "lon":  3.6667},
    48: {"name": "Relizane",           "lat": 35.7400, "lon":  0.5500},
    49: {"name": "Timimoun",           "lat": 29.2667, "lon":  0.2333},
    50: {"name": "Bordj Badji Mokhtar","lat": 21.3833, "lon":  0.9500},
    51: {"name": "Ouled Djellal",      "lat": 34.4333, "lon":  5.0667},
    52: {"name": "Béni Abbès",         "lat": 30.1167, "lon": -2.1667},
    53: {"name": "In Salah",           "lat": 27.2000, "lon":  2.4833},
    54: {"name": "In Guezzam",         "lat": 19.5667, "lon":  5.7667},
    55: {"name": "Touggourt",          "lat": 33.1000, "lon":  6.0667},
    56: {"name": "Djanet",             "lat": 24.5500, "lon":  9.4833},
    57: {"name": "El M'Ghair",         "lat": 33.9500, "lon":  5.9167},
    58: {"name": "El Menia",           "lat": 30.5833, "lon":  2.8833},
}

# Index name -> code for lookup
WILAYA_BY_NAME = {v["name"]: k for k, v in WILAYA_COORDINATES.items()}
# Aliases for common spelling variants
WILAYA_ALIASES = {
    "Bejaia": "Béjaïa", "Tebessa": "Tébessa", "Setif": "Sétif",
    "Saida": "Saïda", "Medea": "Médéa", "Ain Defla": "Aïn Defla",
    "Ain Temouchent": "Aïn Témouchent", "Ghardaia": "Ghardaïa",
    "Tizi-Ouzou": "Tizi Ouzou", "Beni Abbes": "Béni Abbès",
    "Naama": "Naâma", "Boumerdes": "Boumerdès",
    "Sidi Bel Abbes": "Sidi Bel Abbès",
}

def resolve_wilaya(name: str):
    """Returns (code, canonical_name, lat, lon) or raises"""
    name = name.strip()
    canonical = WILAYA_ALIASES.get(name, name)
    code = WILAYA_BY_NAME.get(canonical)
    if code is None:
        raise HTTPException(400, f"Wilaya '{name}' introuvable. Vérifiez l'orthographe.")
    info = WILAYA_COORDINATES[code]
    return code, info["name"], info["lat"], info["lon"]

# ============================================================
# 🧱 TYPES DE SOL (par code wilaya)
# ============================================================
SOIL_MAP = {
    1: "Sols sableux (Erg)",           2: "Sols alluviaux",
    3: "Sols sableux (Erg)",           4: "Vertisols",
    5: "Sols peu évolués d'érosion",   6: "Sols bruns calcaires",
    7: "Sols sableux (Erg)",           8: "Sols sableux (Erg)",
    9: "Sols alluviaux",               10: "Sols bruns calcaires",
    11: "Sols minéraux bruts (Reg)",   12: "Sols bruns calcaires",
    13: "Sols bruns calcaires",        14: "Sols bruns calcaires",
    15: "Sols peu évolués d'érosion",  16: "Sols alluviaux",
    17: "Sols bruns calcaires",        18: "Sols bruns calcaires",
    19: "Sols bruns calcaires",        20: "Sols bruns calcaires",
    21: "Sols bruns calcaires",        22: "Sols bruns calcaires",
    23: "Sols alluviaux",              24: "Vertisols",
    25: "Vertisols",                   26: "Sols bruns calcaires",
    27: "Sols bruns calcaires",        28: "Sols bruns calcaires",
    29: "Sols bruns calcaires",        30: "Sols sableux (Erg)",
    31: "Sols bruns calcaires",        32: "Sols bruns calcaires",
    33: "Sols minéraux bruts (Reg)",   34: "Sols bruns calcaires",
    35: "Sols bruns calcaires",        36: "Sols hydromorphes (Oasis)",
    37: "Sols minéraux bruts (Reg)",   38: "Sols bruns calcaires",
    39: "Sols sableux (Erg)",          40: "Sols bruns calcaires",
    41: "Sols bruns calcaires",        42: "Sols alluviaux",
    43: "Vertisols",                   44: "Sols alluviaux",
    45: "Sols bruns calcaires",        46: "Sols bruns calcaires",
    47: "Sols hydromorphes (Oasis)",   48: "Sols bruns calcaires",
    49: "Sols sableux (Erg)",          50: "Sols minéraux bruts (Reg)",
    51: "Sols sableux (Erg)",          52: "Sols sableux (Erg)",
    53: "Sols minéraux bruts (Reg)",   54: "Sols minéraux bruts (Reg)",
    55: "Sols hydromorphes (Oasis)",   56: "Sols minéraux bruts (Reg)",
    57: "Sols hydromorphes (Oasis)",   58: "Sols sableux (Erg)",
}

SOIL_WATER_FACTOR = {
    "Sols sableux (Erg)":           {"factor": 1.35, "irrigation": "Goutte-à-goutte", "retention": "Très faible"},
    "Sols alluviaux":               {"factor": 0.90, "irrigation": "Aspersion ou gravitaire", "retention": "Élevée"},
    "Sols bruns calcaires":         {"factor": 1.00, "irrigation": "Aspersion", "retention": "Moyenne"},
    "Vertisols":                    {"factor": 0.80, "irrigation": "Gravitaire contrôlé", "retention": "Très élevée"},
    "Sols peu évolués d'érosion":   {"factor": 1.10, "irrigation": "Micro-aspersion", "retention": "Faible"},
    "Sols hydromorphes (Oasis)":    {"factor": 0.85, "irrigation": "Submersion / oasis", "retention": "Très élevée"},
    "Sols minéraux bruts (Reg)":    {"factor": 1.50, "irrigation": "Hydroponique / goutte-à-goutte intensif", "retention": "Nulle"},
}

# ============================================================
# 🌾 50+ CULTURES AVEC DONNÉES COMPLÈTES
# ============================================================
CULTURES_DATA = {
    # --- Céréales ---
    "Blé dur": {
        "fr": "Blé dur", "ar": "القمح الصلب",
        "kc_ini": 0.40, "kc_mid": 1.15, "kc_end": 0.40, "zr": 1.0, "cycle_jours": 180,
        "stades": {"Initial": (0,40), "Développement": (40,100), "Milieu": (100,150), "Fin": (150,180)},
        "besoin_base": 5.0, "temp_min": 5, "temp_opt": 18, "temp_max": 32,
        "pluie_min_annuelle": 300, "cat": "Céréales",
        "conseil": "Semer en octobre–novembre. Éviter la verse par surirrigaton."
    },
    "Blé tendre": {
        "fr": "Blé tendre", "ar": "القمح اللين",
        "kc_ini": 0.40, "kc_mid": 1.15, "kc_end": 0.40, "zr": 1.0, "cycle_jours": 175,
        "stades": {"Initial": (0,38), "Développement": (38,95), "Milieu": (95,145), "Fin": (145,175)},
        "besoin_base": 5.0, "temp_min": 4, "temp_opt": 17, "temp_max": 30,
        "pluie_min_annuelle": 350, "cat": "Céréales",
        "conseil": "Variétés tolérantes à la sécheresse recommandées pour les hauts-plateaux."
    },
    "Orge": {
        "fr": "Orge", "ar": "الشعير",
        "kc_ini": 0.35, "kc_mid": 1.10, "kc_end": 0.35, "zr": 0.9, "cycle_jours": 150,
        "stades": {"Initial": (0,30), "Développement": (30,80), "Milieu": (80,120), "Fin": (120,150)},
        "besoin_base": 4.5, "temp_min": 3, "temp_opt": 16, "temp_max": 30,
        "pluie_min_annuelle": 250, "cat": "Céréales",
        "conseil": "Culture très résistante à la sécheresse. Idéale pour les zones semi-arides."
    },
    "Maïs": {
        "fr": "Maïs", "ar": "الذرة",
        "kc_ini": 0.30, "kc_mid": 1.20, "kc_end": 0.60, "zr": 0.9, "cycle_jours": 130,
        "stades": {"Initial": (0,30), "Développement": (30,70), "Milieu": (70,110), "Fin": (110,130)},
        "besoin_base": 6.5, "temp_min": 10, "temp_opt": 25, "temp_max": 38,
        "pluie_min_annuelle": 500, "cat": "Céréales",
        "conseil": "Irrigation critique à la floraison. Éviter le stress hydrique en phase de milieu."
    },
    "Sorgho": {
        "fr": "Sorgho", "ar": "الذرة البيضاء",
        "kc_ini": 0.35, "kc_mid": 1.10, "kc_end": 0.55, "zr": 1.0, "cycle_jours": 120,
        "stades": {"Initial": (0,25), "Développement": (25,65), "Milieu": (65,100), "Fin": (100,120)},
        "besoin_base": 5.0, "temp_min": 15, "temp_opt": 30, "temp_max": 40,
        "pluie_min_annuelle": 300, "cat": "Céréales",
        "conseil": "Très tolérant à la chaleur et à la sécheresse. Adapté aux zones pré-sahariennes."
    },
    "Avoine": {
        "fr": "Avoine", "ar": "الشوفان",
        "kc_ini": 0.35, "kc_mid": 1.10, "kc_end": 0.35, "zr": 0.9, "cycle_jours": 140,
        "stades": {"Initial": (0,30), "Développement": (30,75), "Milieu": (75,115), "Fin": (115,140)},
        "besoin_base": 4.5, "temp_min": 3, "temp_opt": 15, "temp_max": 28,
        "pluie_min_annuelle": 400, "cat": "Céréales",
        "conseil": "Préfère les zones humides. Bonne rotation avec blé pour briser le cycle des maladies."
    },
    # --- Maraîchage ---
    "Tomate": {
        "fr": "Tomate", "ar": "الطماطم",
        "kc_ini": 0.60, "kc_mid": 1.15, "kc_end": 0.80, "zr": 0.7, "cycle_jours": 120,
        "stades": {"Initial": (0,30), "Développement": (30,70), "Milieu": (70,100), "Fin": (100,120)},
        "besoin_base": 6.0, "temp_min": 10, "temp_opt": 24, "temp_max": 35,
        "pluie_min_annuelle": 400, "cat": "Maraîchage",
        "conseil": "Irrigation régulière pour éviter la BER (nécrose apicale). Mulch conseillé."
    },
    "Pomme de terre": {
        "fr": "Pomme de terre", "ar": "البطاطس",
        "kc_ini": 0.50, "kc_mid": 1.15, "kc_end": 0.75, "zr": 0.6, "cycle_jours": 100,
        "stades": {"Initial": (0,25), "Développement": (25,60), "Milieu": (60,85), "Fin": (85,100)},
        "besoin_base": 5.5, "temp_min": 7, "temp_opt": 18, "temp_max": 28,
        "pluie_min_annuelle": 500, "cat": "Maraîchage",
        "conseil": "Irrigation critique à la tubérisation. Sol bien drainé indispensable."
    },
    "Oignon": {
        "fr": "Oignon", "ar": "البصل",
        "kc_ini": 0.70, "kc_mid": 1.05, "kc_end": 0.75, "zr": 0.5, "cycle_jours": 130,
        "stades": {"Initial": (0,30), "Développement": (30,70), "Milieu": (70,110), "Fin": (110,130)},
        "besoin_base": 5.0, "temp_min": 5, "temp_opt": 20, "temp_max": 30,
        "pluie_min_annuelle": 350, "cat": "Maraîchage",
        "conseil": "Réduire l'irrigation 2 semaines avant récolte pour améliorer la conservation."
    },
    "Ail": {
        "fr": "Ail", "ar": "الثوم",
        "kc_ini": 0.70, "kc_mid": 1.00, "kc_end": 0.70, "zr": 0.5, "cycle_jours": 180,
        "stades": {"Initial": (0,40), "Développement": (40,100), "Milieu": (100,150), "Fin": (150,180)},
        "besoin_base": 4.5, "temp_min": 0, "temp_opt": 18, "temp_max": 28,
        "pluie_min_annuelle": 300, "cat": "Maraîchage",
        "conseil": "Semer en automne. Arrêter l'irrigation quand les feuilles jaunissent."
    },
    "Poivron": {
        "fr": "Poivron", "ar": "الفليفلة",
        "kc_ini": 0.60, "kc_mid": 1.05, "kc_end": 0.90, "zr": 0.6, "cycle_jours": 120,
        "stades": {"Initial": (0,30), "Développement": (30,65), "Milieu": (65,100), "Fin": (100,120)},
        "besoin_base": 5.5, "temp_min": 15, "temp_opt": 25, "temp_max": 35,
        "pluie_min_annuelle": 400, "cat": "Maraîchage",
        "conseil": "Sensible au stress hydrique. Irrigation goutte-à-goutte recommandée."
    },
    "Courgette": {
        "fr": "Courgette", "ar": "الكوسة",
        "kc_ini": 0.50, "kc_mid": 1.00, "kc_end": 0.80, "zr": 0.6, "cycle_jours": 75,
        "stades": {"Initial": (0,20), "Développement": (20,40), "Milieu": (40,60), "Fin": (60,75)},
        "besoin_base": 5.0, "temp_min": 15, "temp_opt": 25, "temp_max": 36,
        "pluie_min_annuelle": 350, "cat": "Maraîchage",
        "conseil": "Cycle court. Production en été avec irrigation régulière."
    },
    "Aubergine": {
        "fr": "Aubergine", "ar": "الباذنجان",
        "kc_ini": 0.60, "kc_mid": 1.05, "kc_end": 0.90, "zr": 0.7, "cycle_jours": 130,
        "stades": {"Initial": (0,30), "Développement": (30,70), "Milieu": (70,110), "Fin": (110,130)},
        "besoin_base": 5.5, "temp_min": 18, "temp_opt": 28, "temp_max": 38,
        "pluie_min_annuelle": 400, "cat": "Maraîchage",
        "conseil": "Culture chaude. Éviter l'engorgement qui provoque la pourriture des racines."
    },
    "Carotte": {
        "fr": "Carotte", "ar": "الجزر",
        "kc_ini": 0.70, "kc_mid": 1.05, "kc_end": 0.95, "zr": 0.5, "cycle_jours": 100,
        "stades": {"Initial": (0,25), "Développement": (25,55), "Milieu": (55,80), "Fin": (80,100)},
        "besoin_base": 4.5, "temp_min": 5, "temp_opt": 18, "temp_max": 28,
        "pluie_min_annuelle": 300, "cat": "Maraîchage",
        "conseil": "Sol profond et meuble. Irrigation uniforme pour racines bien formées."
    },
    "Laitue": {
        "fr": "Laitue", "ar": "الخس",
        "kc_ini": 0.70, "kc_mid": 1.00, "kc_end": 0.95, "zr": 0.3, "cycle_jours": 65,
        "stades": {"Initial": (0,15), "Développement": (15,35), "Milieu": (35,55), "Fin": (55,65)},
        "besoin_base": 4.0, "temp_min": 5, "temp_opt": 18, "temp_max": 26,
        "pluie_min_annuelle": 300, "cat": "Maraîchage",
        "conseil": "Cycle très court. Éviter chaleur excessive qui provoque la montée en graine."
    },
    "Pastèque": {
        "fr": "Pastèque", "ar": "البطيخ",
        "kc_ini": 0.40, "kc_mid": 1.00, "kc_end": 0.75, "zr": 0.8, "cycle_jours": 90,
        "stades": {"Initial": (0,20), "Développement": (20,50), "Milieu": (50,75), "Fin": (75,90)},
        "besoin_base": 5.5, "temp_min": 18, "temp_opt": 28, "temp_max": 38,
        "pluie_min_annuelle": 300, "cat": "Maraîchage",
        "conseil": "Réduire irrigation à maturité pour améliorer sucrosité. Sol sableux idéal."
    },
    "Melon": {
        "fr": "Melon", "ar": "الشمام",
        "kc_ini": 0.45, "kc_mid": 1.05, "kc_end": 0.75, "zr": 0.8, "cycle_jours": 90,
        "stades": {"Initial": (0,20), "Développement": (20,50), "Milieu": (50,75), "Fin": (75,90)},
        "besoin_base": 5.5, "temp_min": 18, "temp_opt": 28, "temp_max": 38,
        "pluie_min_annuelle": 300, "cat": "Maraîchage",
        "conseil": "Identique pastèque. Irrigation drip très conseillée."
    },
    "Piment fort": {
        "fr": "Piment fort", "ar": "الفلفل الحار",
        "kc_ini": 0.60, "kc_mid": 1.05, "kc_end": 0.90, "zr": 0.6, "cycle_jours": 130,
        "stades": {"Initial": (0,30), "Développement": (30,70), "Milieu": (70,110), "Fin": (110,130)},
        "besoin_base": 5.0, "temp_min": 16, "temp_opt": 27, "temp_max": 37,
        "pluie_min_annuelle": 350, "cat": "Maraîchage",
        "conseil": "Variétés locales très adaptées au climat algérien. Bon marché d'export."
    },
    "Navet": {
        "fr": "Navet", "ar": "اللفت",
        "kc_ini": 0.50, "kc_mid": 1.10, "kc_end": 0.90, "zr": 0.5, "cycle_jours": 70,
        "stades": {"Initial": (0,20), "Développement": (20,40), "Milieu": (40,60), "Fin": (60,70)},
        "besoin_base": 4.0, "temp_min": 5, "temp_opt": 17, "temp_max": 25,
        "pluie_min_annuelle": 300, "cat": "Maraîchage",
        "conseil": "Culture d'automne-hiver. Résistant au froid."
    },
    # --- Légumineuses ---
    "Pois chiche": {
        "fr": "Pois chiche", "ar": "الحمص",
        "kc_ini": 0.40, "kc_mid": 1.00, "kc_end": 0.35, "zr": 0.8, "cycle_jours": 100,
        "stades": {"Initial": (0,25), "Développement": (25,55), "Milieu": (55,80), "Fin": (80,100)},
        "besoin_base": 4.0, "temp_min": 5, "temp_opt": 22, "temp_max": 32,
        "pluie_min_annuelle": 250, "cat": "Légumineuses",
        "conseil": "Culture pluviale possible. Excellente culture de rotation fixatrice d'azote."
    },
    "Lentille": {
        "fr": "Lentille", "ar": "العدس",
        "kc_ini": 0.40, "kc_mid": 1.05, "kc_end": 0.30, "zr": 0.7, "cycle_jours": 110,
        "stades": {"Initial": (0,25), "Développement": (25,60), "Milieu": (60,90), "Fin": (90,110)},
        "besoin_base": 4.0, "temp_min": 5, "temp_opt": 18, "temp_max": 28,
        "pluie_min_annuelle": 300, "cat": "Légumineuses",
        "conseil": "Très peu exigeante en eau. Résiste bien au froid et à la sécheresse."
    },
    "Fève": {
        "fr": "Fève", "ar": "الفول",
        "kc_ini": 0.50, "kc_mid": 1.15, "kc_end": 0.30, "zr": 0.7, "cycle_jours": 130,
        "stades": {"Initial": (0,30), "Développement": (30,70), "Milieu": (70,105), "Fin": (105,130)},
        "besoin_base": 5.0, "temp_min": 5, "temp_opt": 18, "temp_max": 28,
        "pluie_min_annuelle": 400, "cat": "Légumineuses",
        "conseil": "Semer en automne-hiver. Très bonne culture pour améliorer la structure du sol."
    },
    "Haricot vert": {
        "fr": "Haricot vert", "ar": "الفاصوليا الخضراء",
        "kc_ini": 0.40, "kc_mid": 1.15, "kc_end": 0.35, "zr": 0.6, "cycle_jours": 70,
        "stades": {"Initial": (0,20), "Développement": (20,40), "Milieu": (40,60), "Fin": (60,70)},
        "besoin_base": 4.5, "temp_min": 10, "temp_opt": 22, "temp_max": 32,
        "pluie_min_annuelle": 400, "cat": "Légumineuses",
        "conseil": "Sensible au gel. Production printanière ou estivale."
    },
    "Petits pois": {
        "fr": "Petits pois", "ar": "الجلبانة",
        "kc_ini": 0.50, "kc_mid": 1.15, "kc_end": 1.10, "zr": 0.6, "cycle_jours": 80,
        "stades": {"Initial": (0,20), "Développement": (20,45), "Milieu": (45,65), "Fin": (65,80)},
        "besoin_base": 4.5, "temp_min": 5, "temp_opt": 18, "temp_max": 25,
        "pluie_min_annuelle": 350, "cat": "Légumineuses",
        "conseil": "Culture de saison fraîche. Irrigation critique à la floraison."
    },
    # --- Arboriculture ---
    "Olivier": {
        "fr": "Olivier", "ar": "الزيتون",
        "kc_ini": 0.65, "kc_mid": 0.70, "kc_end": 0.65, "zr": 1.2, "cycle_jours": 365,
        "stades": {"Initial": (0,90), "Développement": (90,180), "Milieu": (180,270), "Fin": (270,365)},
        "besoin_base": 4.0, "temp_min": -5, "temp_opt": 22, "temp_max": 40,
        "pluie_min_annuelle": 200, "cat": "Arboriculture",
        "conseil": "Résistant à la sécheresse. Irrigation d'appoint en été améliore le rendement de 30-40%."
    },
    "Palmier dattier": {
        "fr": "Palmier dattier", "ar": "النخيل",
        "kc_ini": 0.80, "kc_mid": 1.05, "kc_end": 0.85, "zr": 1.5, "cycle_jours": 365,
        "stades": {"Initial": (0,90), "Développement": (90,200), "Milieu": (200,300), "Fin": (300,365)},
        "besoin_base": 8.0, "temp_min": 5, "temp_opt": 35, "temp_max": 50,
        "pluie_min_annuelle": 50, "cat": "Arboriculture",
        "conseil": "Irrigation intensive indispensable dans les régions sahariennes. Tolérant au sel."
    },
    "Figuier": {
        "fr": "Figuier", "ar": "التين",
        "kc_ini": 0.50, "kc_mid": 0.85, "kc_end": 0.70, "zr": 1.2, "cycle_jours": 210,
        "stades": {"Initial": (0,60), "Développement": (60,120), "Milieu": (120,180), "Fin": (180,210)},
        "besoin_base": 4.5, "temp_min": 0, "temp_opt": 28, "temp_max": 40,
        "pluie_min_annuelle": 250, "cat": "Arboriculture",
        "conseil": "Arbre très résistant à la sécheresse. Culture traditionnelle méditerranéenne."
    },
    "Grenadier": {
        "fr": "Grenadier", "ar": "الرمان",
        "kc_ini": 0.50, "kc_mid": 0.85, "kc_end": 0.70, "zr": 1.0, "cycle_jours": 200,
        "stades": {"Initial": (0,50), "Développement": (50,110), "Milieu": (110,170), "Fin": (170,200)},
        "besoin_base": 4.5, "temp_min": -5, "temp_opt": 25, "temp_max": 40,
        "pluie_min_annuelle": 200, "cat": "Arboriculture",
        "conseil": "Très rustique. Produit mieux avec 2-3 irrigations en été."
    },
    "Vigne": {
        "fr": "Vigne", "ar": "الكرمة",
        "kc_ini": 0.30, "kc_mid": 0.85, "kc_end": 0.45, "zr": 1.0, "cycle_jours": 180,
        "stades": {"Initial": (0,40), "Développement": (40,100), "Milieu": (100,150), "Fin": (150,180)},
        "besoin_base": 4.5, "temp_min": -2, "temp_opt": 23, "temp_max": 38,
        "pluie_min_annuelle": 300, "cat": "Arboriculture",
        "conseil": "Réduire l'eau avant vendange pour concentrer les sucres. Sol drainé impératif."
    },
    "Amandier": {
        "fr": "Amandier", "ar": "اللوز",
        "kc_ini": 0.40, "kc_mid": 0.90, "kc_end": 0.65, "zr": 1.2, "cycle_jours": 200,
        "stades": {"Initial": (0,50), "Développement": (50,110), "Milieu": (110,170), "Fin": (170,200)},
        "besoin_base": 4.0, "temp_min": -3, "temp_opt": 22, "temp_max": 38,
        "pluie_min_annuelle": 250, "cat": "Arboriculture",
        "conseil": "Floraison précoce. Risque de gel printanier dans les zones de montagne."
    },
    "Abricotier": {
        "fr": "Abricotier", "ar": "المشمش",
        "kc_ini": 0.45, "kc_mid": 0.90, "kc_end": 0.65, "zr": 1.0, "cycle_jours": 180,
        "stades": {"Initial": (0,45), "Développement": (45,105), "Milieu": (105,155), "Fin": (155,180)},
        "besoin_base": 4.5, "temp_min": -5, "temp_opt": 22, "temp_max": 35,
        "pluie_min_annuelle": 300, "cat": "Arboriculture",
        "conseil": "Irrigation à la nouaison critique. Attention au cloque en régions humides."
    },
    "Pêcher": {
        "fr": "Pêcher", "ar": "الخوخ",
        "kc_ini": 0.45, "kc_mid": 1.00, "kc_end": 0.75, "zr": 1.0, "cycle_jours": 180,
        "stades": {"Initial": (0,45), "Développement": (45,105), "Milieu": (105,155), "Fin": (155,180)},
        "besoin_base": 5.0, "temp_min": -5, "temp_opt": 22, "temp_max": 35,
        "pluie_min_annuelle": 400, "cat": "Arboriculture",
        "conseil": "Exige un nombre d'heures de froid (chilling) pour la levée de dormance."
    },
    "Prunier": {
        "fr": "Prunier", "ar": "البرقوق",
        "kc_ini": 0.45, "kc_mid": 0.90, "kc_end": 0.65, "zr": 1.0, "cycle_jours": 175,
        "stades": {"Initial": (0,40), "Développement": (40,100), "Milieu": (100,148), "Fin": (148,175)},
        "besoin_base": 4.5, "temp_min": -5, "temp_opt": 20, "temp_max": 34,
        "pluie_min_annuelle": 400, "cat": "Arboriculture",
        "conseil": "Sol profond et bien drainé. Taille annuelle indispensable."
    },
    "Cerisier": {
        "fr": "Cerisier", "ar": "الكرز",
        "kc_ini": 0.45, "kc_mid": 0.90, "kc_end": 0.60, "zr": 1.0, "cycle_jours": 160,
        "stades": {"Initial": (0,40), "Développement": (40,95), "Milieu": (95,140), "Fin": (140,160)},
        "besoin_base": 4.5, "temp_min": -5, "temp_opt": 18, "temp_max": 32,
        "pluie_min_annuelle": 500, "cat": "Arboriculture",
        "conseil": "Adapté aux zones montagneuses de Kabylie, Aurès. Craint les pluies à maturité."
    },
    "Agrumes (Oranger)": {
        "fr": "Agrumes (Oranger)", "ar": "البرتقال",
        "kc_ini": 0.65, "kc_mid": 0.70, "kc_end": 0.65, "zr": 1.0, "cycle_jours": 365,
        "stades": {"Initial": (0,90), "Développement": (90,180), "Milieu": (180,270), "Fin": (270,365)},
        "besoin_base": 5.5, "temp_min": 5, "temp_opt": 25, "temp_max": 38,
        "pluie_min_annuelle": 500, "cat": "Arboriculture",
        "conseil": "Irriguer régulièrement en été. Zone littorale Nord idéale (Mitidja, Oranie)."
    },
    "Citronnier": {
        "fr": "Citronnier", "ar": "الليمون",
        "kc_ini": 0.65, "kc_mid": 0.70, "kc_end": 0.65, "zr": 1.0, "cycle_jours": 365,
        "stades": {"Initial": (0,90), "Développement": (90,180), "Milieu": (180,270), "Fin": (270,365)},
        "besoin_base": 5.0, "temp_min": 7, "temp_opt": 26, "temp_max": 38,
        "pluie_min_annuelle": 500, "cat": "Arboriculture",
        "conseil": "Plus résistant à la chaleur que l'oranger. Irriguer en profondeur."
    },
    # --- Cultures industrielles ---
    "Tournesol": {
        "fr": "Tournesol", "ar": "عباد الشمس",
        "kc_ini": 0.35, "kc_mid": 1.15, "kc_end": 0.35, "zr": 1.0, "cycle_jours": 130,
        "stades": {"Initial": (0,30), "Développement": (30,70), "Milieu": (70,110), "Fin": (110,130)},
        "besoin_base": 5.5, "temp_min": 8, "temp_opt": 24, "temp_max": 35,
        "pluie_min_annuelle": 350, "cat": "Industrie",
        "conseil": "Racines profondes, résistant à la sécheresse. Bon précédent cultural."
    },
    "Betterave sucrière": {
        "fr": "Betterave sucrière", "ar": "الشمندر السكري",
        "kc_ini": 0.35, "kc_mid": 1.20, "kc_end": 0.70, "zr": 1.0, "cycle_jours": 170,
        "stades": {"Initial": (0,40), "Développement": (40,90), "Milieu": (90,145), "Fin": (145,170)},
        "besoin_base": 6.0, "temp_min": 5, "temp_opt": 20, "temp_max": 28,
        "pluie_min_annuelle": 450, "cat": "Industrie",
        "conseil": "Sol profond sans cailloux. Culture stratégique pour l'agro-industrie algérienne."
    },
    "Coton": {
        "fr": "Coton", "ar": "القطن",
        "kc_ini": 0.35, "kc_mid": 1.20, "kc_end": 0.50, "zr": 1.0, "cycle_jours": 180,
        "stades": {"Initial": (0,45), "Développement": (45,100), "Milieu": (100,150), "Fin": (150,180)},
        "besoin_base": 7.0, "temp_min": 18, "temp_opt": 32, "temp_max": 42,
        "pluie_min_annuelle": 600, "cat": "Industrie",
        "conseil": "Culture potentielle pour le Sahara avec irrigation. Zones chaudes du Sud-Ouest."
    },
    "Tabac": {
        "fr": "Tabac", "ar": "التبغ",
        "kc_ini": 0.30, "kc_mid": 1.00, "kc_end": 0.90, "zr": 0.7, "cycle_jours": 120,
        "stades": {"Initial": (0,30), "Développement": (30,65), "Milieu": (65,95), "Fin": (95,120)},
        "besoin_base": 5.0, "temp_min": 18, "temp_opt": 26, "temp_max": 35,
        "pluie_min_annuelle": 500, "cat": "Industrie",
        "conseil": "Culture dans le Nord-Est (Jijel, Skikda). Sol léger bien drainé."
    },
    # --- Cultures fourragères ---
    "Luzerne": {
        "fr": "Luzerne", "ar": "البرسيم",
        "kc_ini": 0.40, "kc_mid": 1.20, "kc_end": 1.15, "zr": 1.0, "cycle_jours": 365,
        "stades": {"Initial": (0,90), "Développement": (90,180), "Milieu": (180,270), "Fin": (270,365)},
        "besoin_base": 7.0, "temp_min": 5, "temp_opt": 22, "temp_max": 35,
        "pluie_min_annuelle": 400, "cat": "Fourrages",
        "conseil": "6-8 coupes/an. Excellente plante fixatrice d'azote. Irriguer après chaque coupe."
    },
    "Vesce-avoine": {
        "fr": "Vesce-avoine", "ar": "الجلبانة والشوفان",
        "kc_ini": 0.35, "kc_mid": 1.05, "kc_end": 0.40, "zr": 0.8, "cycle_jours": 120,
        "stades": {"Initial": (0,30), "Développement": (30,65), "Milieu": (65,100), "Fin": (100,120)},
        "besoin_base": 4.5, "temp_min": 3, "temp_opt": 15, "temp_max": 25,
        "pluie_min_annuelle": 300, "cat": "Fourrages",
        "conseil": "Mélange fourrager d'automne-hiver. Bonne valeur nutritive."
    },
    # --- Cultures sahariennesOasis ---
    "Henné": {
        "fr": "Henné", "ar": "الحناء",
        "kc_ini": 0.50, "kc_mid": 0.85, "kc_end": 0.70, "zr": 0.8, "cycle_jours": 150,
        "stades": {"Initial": (0,35), "Développement": (35,80), "Milieu": (80,120), "Fin": (120,150)},
        "besoin_base": 5.5, "temp_min": 15, "temp_opt": 32, "temp_max": 45,
        "pluie_min_annuelle": 50, "cat": "Oasis",
        "conseil": "Culture oasienne traditionnelle. Résiste bien à la chaleur extrême."
    },
    "Tomate saharienne": {
        "fr": "Tomate saharienne", "ar": "طماطم صحراوية",
        "kc_ini": 0.60, "kc_mid": 1.15, "kc_end": 0.80, "zr": 0.7, "cycle_jours": 100,
        "stades": {"Initial": (0,25), "Développement": (25,60), "Milieu": (60,85), "Fin": (85,100)},
        "besoin_base": 7.0, "temp_min": 15, "temp_opt": 30, "temp_max": 42,
        "pluie_min_annuelle": 50, "cat": "Oasis",
        "conseil": "Production hivernale sous serres ou en plein air dans les oasis du Sud."
    },
    # --- Épices et aromates ---
    "Coriandre": {
        "fr": "Coriandre", "ar": "الكزبرة",
        "kc_ini": 0.60, "kc_mid": 1.00, "kc_end": 0.80, "zr": 0.4, "cycle_jours": 60,
        "stades": {"Initial": (0,15), "Développement": (15,35), "Milieu": (35,50), "Fin": (50,60)},
        "besoin_base": 3.5, "temp_min": 10, "temp_opt": 22, "temp_max": 30,
        "pluie_min_annuelle": 250, "cat": "Aromates",
        "conseil": "Cycle très court. Possible en automne et printemps."
    },
    "Aneth": {
        "fr": "Aneth", "ar": "الشبت",
        "kc_ini": 0.60, "kc_mid": 1.00, "kc_end": 0.80, "zr": 0.4, "cycle_jours": 65,
        "stades": {"Initial": (0,15), "Développement": (15,38), "Milieu": (38,55), "Fin": (55,65)},
        "besoin_base": 3.5, "temp_min": 5, "temp_opt": 20, "temp_max": 28,
        "pluie_min_annuelle": 250, "cat": "Aromates",
        "conseil": "Sol léger et bien drainé. Semer successivement pour étaler la récolte."
    },
    "Cumin": {
        "fr": "Cumin", "ar": "الكمون",
        "kc_ini": 0.40, "kc_mid": 0.90, "kc_end": 0.50, "zr": 0.5, "cycle_jours": 110,
        "stades": {"Initial": (0,25), "Développement": (25,60), "Milieu": (60,90), "Fin": (90,110)},
        "besoin_base": 3.5, "temp_min": 10, "temp_opt": 24, "temp_max": 34,
        "pluie_min_annuelle": 200, "cat": "Aromates",
        "conseil": "Résistant à la sécheresse. Valeur commerciale élevée."
    },
    # --- Fleurs / plantes ---
    "Géranium rosat": {
        "fr": "Géranium rosat", "ar": "الجرانيوم العطري",
        "kc_ini": 0.50, "kc_mid": 0.95, "kc_end": 0.80, "zr": 0.5, "cycle_jours": 180,
        "stades": {"Initial": (0,40), "Développement": (40,100), "Milieu": (100,155), "Fin": (155,180)},
        "besoin_base": 4.5, "temp_min": 5, "temp_opt": 22, "temp_max": 32,
        "pluie_min_annuelle": 400, "cat": "Aromates",
        "conseil": "Culture à haute valeur ajoutée pour l'extraction d'huile essentielle."
    },
    # --- Cultures sous-serre ---
    "Concombre sous serre": {
        "fr": "Concombre sous serre", "ar": "الخيار تحت البيت البلاستيكي",
        "kc_ini": 0.60, "kc_mid": 1.00, "kc_end": 0.80, "zr": 0.5, "cycle_jours": 90,
        "stades": {"Initial": (0,20), "Développement": (20,50), "Milieu": (50,75), "Fin": (75,90)},
        "besoin_base": 6.0, "temp_min": 15, "temp_opt": 26, "temp_max": 35,
        "pluie_min_annuelle": 0, "cat": "Sous serre",
        "conseil": "Irrigation goutte-à-goutte sous serre. Contrôle hygrométrie important."
    },
    "Tomate sous serre": {
        "fr": "Tomate sous serre", "ar": "طماطم تحت البيت البلاستيكي",
        "kc_ini": 0.60, "kc_mid": 1.15, "kc_end": 0.80, "zr": 0.7, "cycle_jours": 150,
        "stades": {"Initial": (0,35), "Développement": (35,80), "Milieu": (80,125), "Fin": (125,150)},
        "besoin_base": 6.5, "temp_min": 15, "temp_opt": 24, "temp_max": 32,
        "pluie_min_annuelle": 0, "cat": "Sous serre",
        "conseil": "Production hors-saison possible. Fertigation recommandée."
    },
    # --- Autres ---
    "Safran": {
        "fr": "Safran", "ar": "الزعفران",
        "kc_ini": 0.50, "kc_mid": 0.85, "kc_end": 0.50, "zr": 0.4, "cycle_jours": 210,
        "stades": {"Initial": (0,50), "Développement": (50,100), "Milieu": (100,170), "Fin": (170,210)},
        "besoin_base": 3.5, "temp_min": 5, "temp_opt": 18, "temp_max": 28,
        "pluie_min_annuelle": 200, "cat": "Aromates",
        "conseil": "Potentiel de développement énorme en Algérie. Culture à très haute valeur ajoutée."
    },
    "Artichaut": {
        "fr": "Artichaut", "ar": "الخرشوف",
        "kc_ini": 0.50, "kc_mid": 1.00, "kc_end": 0.90, "zr": 0.7, "cycle_jours": 180,
        "stades": {"Initial": (0,45), "Développement": (45,100), "Milieu": (100,150), "Fin": (150,180)},
        "besoin_base": 5.5, "temp_min": 5, "temp_opt": 20, "temp_max": 30,
        "pluie_min_annuelle": 400, "cat": "Maraîchage",
        "conseil": "Culture méditerranéenne typique. Zones côtières et Mitidja idéales."
    },
}

# ============================================================
# 🌦️ MÉTÉO RÉELLE via Open-Meteo (gratuit, sans clé API)
# ============================================================
OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
OPEN_METEO_HISTORICAL_URL = "https://archive-api.open-meteo.com/v1/archive"

async def fetch_real_weather(lat: float, lon: float):
    """Fetch 7-day forecast + past 7 days from Open-Meteo (free, no key)"""
    today = datetime.now().date()
    past_start = (today - timedelta(days=8)).isoformat()
    past_end   = (today - timedelta(days=1)).isoformat()

    async with httpx.AsyncClient(timeout=15) as client:
        # 7-day forecast
        forecast_params = {
            "latitude": lat, "longitude": lon,
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max,weathercode",
            "forecast_days": 7,
            "timezone": "Africa/Algiers"
        }
        # Past 8 days (historical)
        hist_params = {
            "latitude": lat, "longitude": lon,
            "start_date": past_start, "end_date": past_end,
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
            "timezone": "Africa/Algiers"
        }

        try:
            forecast_resp, hist_resp = await asyncio.gather(
                client.get(OPEN_METEO_URL, params=forecast_params),
                client.get(OPEN_METEO_HISTORICAL_URL, params=hist_params)
            )
            forecast_data = forecast_resp.json()
            hist_data = hist_resp.json()
        except Exception as e:
            # Fallback to empty
            return None, None

    return forecast_data, hist_data

def parse_forecast(forecast_data: dict, hist_data: dict):
    """Parse Open-Meteo responses into usable structures"""
    if forecast_data is None:
        return [], [], 0

    fd = forecast_data.get("daily", {})
    dates      = fd.get("time", [])
    tmax       = fd.get("temperature_2m_max", [])
    tmin       = fd.get("temperature_2m_min", [])
    precip     = fd.get("precipitation_sum", [])
    wcode      = fd.get("weathercode", [])
    wind       = fd.get("wind_speed_10m_max", [])

    WMO_LABELS = {
        0: "☀️ Ciel dégagé", 1: "🌤 Peu nuageux", 2: "⛅ Partiellement nuageux",
        3: "☁️ Couvert", 45: "🌫 Brouillard", 51: "🌦 Bruine légère",
        53: "🌧 Bruine", 55: "🌧 Bruine forte", 61: "🌧 Pluie légère",
        63: "🌧 Pluie modérée", 65: "🌧 Pluie forte", 71: "❄️ Neige légère",
        73: "❄️ Neige", 80: "🌦 Averses", 81: "🌧 Averses modérées",
        82: "⛈ Averses violentes", 95: "⛈ Orage", 96: "⛈ Orage grêle",
    }

    forecast_list = []
    for i, d in enumerate(dates):
        p = float(precip[i]) if i < len(precip) and precip[i] is not None else 0.0
        tx = float(tmax[i]) if i < len(tmax) and tmax[i] is not None else 20.0
        tn = float(tmin[i]) if i < len(tmin) and tmin[i] is not None else 10.0
        wc = int(wcode[i]) if i < len(wcode) and wcode[i] is not None else 0
        w  = float(wind[i]) if i < len(wind) and wind[i] is not None else 0.0
        forecast_list.append({
            "date": d,
            "jour": i + 1,
            "temp_max": round(tx, 1),
            "temp_min": round(tn, 1),
            "temp_moy": round((tx + tn) / 2, 1),
            "precipitation": round(p, 1),
            "a_pluie": p > 0.5,
            "code_meteo": wc,
            "description": WMO_LABELS.get(wc, "Inconnu"),
            "vent_kmh": round(w, 1),
        })

    # Historical - calculate consecutive dry days
    hist_list = []
    jours_sans_pluie = 0
    total_pluie_semaine = 0.0
    if hist_data and "daily" in hist_data:
        hd = hist_data["daily"]
        hp = hd.get("precipitation_sum", [])
        for val in reversed(hp):
            v = float(val) if val is not None else 0.0
            total_pluie_semaine += v
            if v < 0.5:
                jours_sans_pluie += 1
            else:
                break
        hist_list = [
            {"date": hd["time"][i], "precipitation": float(hp[i]) if hp[i] is not None else 0.0}
            for i in range(len(hd.get("time", [])))
        ]

    return forecast_list, hist_list, jours_sans_pluie

# ============================================================
# 💧 MOTEUR DE RECOMMANDATION D'IRRIGATION
# ============================================================
IRRIGATION_TYPES = {
    "Goutte-à-goutte": {
        "description": "Irrigation localisée au pied de chaque plante",
        "efficacite": "90-95%",
        "conseille_pour": ["Sols sableux", "Zones arides", "Maraîchage", "Sous serre"],
        "debit": "1-4 L/h par goutteur",
    },
    "Aspersion": {
        "description": "Diffusion par arroseurs rotatifs sur toute la parcelle",
        "efficacite": "70-80%",
        "conseille_pour": ["Céréales", "Fourrages", "Sols limoneux"],
        "debit": "3-10 mm/h",
    },
    "Micro-aspersion": {
        "description": "Mini-arroseurs à faible débit, rayon réduit",
        "efficacite": "80-90%",
        "conseille_pour": ["Arboriculture", "Sols peu évolués", "Vignes"],
        "debit": "40-200 L/h par arroseur",
    },
    "Gravitaire contrôlé": {
        "description": "Irrigation par rigoles ou bandes avec contrôle du débit",
        "efficacite": "60-70%",
        "conseille_pour": ["Vertisols", "Grandes cultures", "Blé", "Maïs"],
        "debit": "Variable selon pente",
    },
    "Submersion / oasis": {
        "description": "Inondation contrôlée des planches de culture en oasis",
        "efficacite": "50-65%",
        "conseille_pour": ["Palmier dattier", "Cultures oasiennes", "Sols hydromorphes"],
        "debit": "Selon bassins",
    },
    "Hydroponique / goutte-à-goutte intensif": {
        "description": "Culture hors-sol ou irrigation intensifiée pour régions désertiques",
        "efficacite": "95-99%",
        "conseille_pour": ["Sols minéraux bruts", "Régions sahariennes extrêmes"],
        "debit": "Contrôle électronique",
    },
}

class RecommandationEngine:
    def __init__(self, wilaya_name, culture_name, date_plantation_str,
                 forecast, hist, jours_sans_pluie, lat):
        self.wilaya = wilaya_name
        self.culture = culture_name
        self.date_plantation = datetime.strptime(date_plantation_str, "%Y-%m-%d")
        self.forecast = forecast  # list of 7 dicts
        self.hist = hist
        self.jours_sans_pluie = jours_sans_pluie
        self.lat = lat
        self.culture_data = CULTURES_DATA.get(culture_name, CULTURES_DATA["Blé dur"])

    def calculer_stade(self):
        jours = (datetime.now() - self.date_plantation).days
        if jours < 0:
            return "Non planté", 0, self.culture_data['cycle_jours'], jours
        for stade, (debut, fin) in self.culture_data['stades'].items():
            if debut <= jours <= fin:
                pct = int((jours - debut) / (fin - debut) * 100) if fin > debut else 0
                return stade, pct, fin - debut, jours
        if jours > self.culture_data['cycle_jours']:
            return "Cycle terminé", 100, 0, jours
        return "Inconnu", 0, 0, jours

    def get_soil_info(self, soil_type):
        return SOIL_WATER_FACTOR.get(soil_type, SOIL_WATER_FACTOR["Sols bruns calcaires"])

    def _stress_hydrique(self):
        """Score de stress basé sur jours sans pluie + température"""
        stress = min(1.35, 1 + self.jours_sans_pluie / 22)
        if self.forecast:
            avg_temp = np.mean([d["temp_max"] for d in self.forecast[:3]])
            if avg_temp > 35:
                stress = min(1.5, stress * 1.15)
            elif avg_temp > 30:
                stress = min(1.45, stress * 1.08)
        return stress

    def _analyse_pluie_prevue(self):
        """Analyse la pluie prévue sur 7 jours"""
        pluie_j1j2, pluie_j3j4, pluie_j5j7 = 0.0, 0.0, 0.0
        premier_jour_pluie = None
        total_pluie_7j = 0.0

        for p in self.forecast:
            j = p["jour"]
            precip = p["precipitation"]
            total_pluie_7j += precip
            if precip > 0.5 and premier_jour_pluie is None:
                premier_jour_pluie = p
            if j <= 2:
                pluie_j1j2 += precip
            elif j <= 4:
                pluie_j3j4 += precip
            else:
                pluie_j5j7 += precip

        return {
            "pluie_j1j2": round(pluie_j1j2, 1),
            "pluie_j3j4": round(pluie_j3j4, 1),
            "pluie_j5j7": round(pluie_j5j7, 1),
            "total_7j": round(total_pluie_7j, 1),
            "premier_jour": premier_jour_pluie,
        }

    def recommander(self, stade, soil_type):
        besoin = self.culture_data["besoin_base"]
        coeff_stade = {
            "Initial": 0.50, "Développement": 0.85, "Milieu": 1.25,
            "Fin": 0.55, "Cycle terminé": 0.20, "Non planté": 0.0,
        }
        c = coeff_stade.get(stade, 0.70)
        stress = self._stress_hydrique()
        soil_info = self.get_soil_info(soil_type)
        facteur_sol = soil_info["factor"]
        type_irrigation = soil_info["irrigation"]

        quantite_base = besoin * c * stress * facteur_sol

        pluie = self._analyse_pluie_prevue()
        pj12 = pluie["pluie_j1j2"]
        pj34 = pluie["pluie_j3j4"]
        total = pluie["total_7j"]

        # Ajustement intelligent par rapport à la pluie
        if pj12 >= 8:
            quantite = 0.0
            urgence = "🟢 AUCUNE"
            raison = f"Forte pluie imminente ({pj12} mm dans 48h) – Irrigation inutile"
            frequence = "Contrôle dans 3-4 jours"
        elif pj12 >= 4:
            quantite = max(0, quantite_base * 0.15)
            urgence = "🟡 TRÈS LÉGÈRE"
            raison = f"Pluie significative prévue ({pj12} mm dans 48h)"
            frequence = "1 arrosage léger si sol très sec"
        elif pj12 >= 1:
            quantite = quantite_base * 0.35
            urgence = "🟡 LÉGÈRE"
            raison = f"Pluie légère prévue ({pj12} mm dans 48h)"
            frequence = "Arrosage réduit, surveiller météo"
        elif pj34 >= 6:
            quantite = quantite_base * 0.40
            urgence = "🟡 LÉGÈRE"
            raison = f"Pluie modérée à venir ({pj34} mm dans 3-4 jours)"
            frequence = "1 arrosage limité maintenant"
        elif pj34 >= 3:
            quantite = quantite_base * 0.60
            urgence = "🟠 MODÉRÉE"
            raison = f"Pluie dans 3-4 jours ({pj34} mm) – Irrigation réduite"
            frequence = "Tous les 3 jours"
        elif total >= 5:
            quantite = quantite_base * 0.75
            urgence = "🟠 NORMALE"
            raison = f"Pluies éparses prévues ({total} mm sur 7j) – Irrigation normale réduite"
            frequence = "Tous les 2-3 jours"
        else:
            quantite = quantite_base
            urgence = "🔴 FORTE"
            raison = f"Aucune pluie significative prévue ({total} mm sur 7j) – Stress hydrique"
            frequence = "Quotidienne ou tous les 2 jours"

        quantite = round(max(0, quantite), 1)

        # Conseils détaillés
        temp_avg = np.mean([d["temp_max"] for d in self.forecast[:3]]) if self.forecast else 20
        conseilsD = []
        if temp_avg > 35:
            conseilsD.append("🌡️ Canicule détectée: arroser tôt le matin (5h-7h) ou en soirée après 19h")
        if self.jours_sans_pluie > 10:
            conseilsD.append(f"⚠️ {self.jours_sans_pluie} jours sans pluie: vérifier le point de flétrissement")
        if stade == "Milieu":
            conseilsD.append("🌿 Phase critique – ne jamais laisser le sol se dessécher complètement")
        if stade == "Fin":
            conseilsD.append("📉 Fin de cycle: réduire progressivement l'irrigation pour favoriser la maturation")
        conseilsD.append(f"💧 Méthode recommandée: {type_irrigation}")
        conseilsD.append(self.culture_data.get("conseil", ""))

        irrig_detail = IRRIGATION_TYPES.get(type_irrigation, {})

        return {
            "quantite_eau": quantite,
            "niveau_urgence": urgence,
            "raison_ajustement": raison,
            "frequence_recommandee": frequence,
            "conseils_detailles": conseilsD,
            "type_irrigation": type_irrigation,
            "irrigation_detail": irrig_detail,
            "analyse_pluie": pluie,
            "stress_hydrique": round(stress, 2),
            "temp_moyenne_3j": round(float(temp_avg), 1),
        }

# ============================================================
# 🔁 ENDPOINTS API
# ============================================================

@app.get("/wilayas")
def get_wilayas():
    return {
        "count": 58,
        "wilayas": [
            {"code": k, "name": v["name"], "lat": v["lat"], "lon": v["lon"], "soil": SOIL_MAP.get(k, "?")}
            for k, v in WILAYA_COORDINATES.items()
        ]
    }

@app.get("/cultures")
def get_cultures():
    return {
        "count": len(CULTURES_DATA),
        "categories": list({v["cat"] for v in CULTURES_DATA.values()}),
        "cultures": [
            {"name": k, "ar": v["ar"], "cat": v["cat"],
             "cycle_jours": v["cycle_jours"], "temp_opt": v["temp_opt"]}
            for k, v in CULTURES_DATA.items()
        ]
    }

@app.get("/weather")
async def get_weather(wilaya: str):
    code, name, lat, lon = resolve_wilaya(wilaya)
    forecast_data, hist_data = await fetch_real_weather(lat, lon)
    forecast, hist, jours_sans = parse_forecast(forecast_data, hist_data)
    return {
        "wilaya": name, "lat": lat, "lon": lon,
        "jours_sans_pluie_consecutifs": jours_sans,
        "forecast_7j": forecast,
        "historique_8j": hist,
    }

@app.get("/irrigation")
async def get_irrigation(wilaya: str, culture: str, date_plantation: str):
    # Resolve wilaya
    code, name, lat, lon = resolve_wilaya(wilaya)
    if culture not in CULTURES_DATA:
        raise HTTPException(400, f"Culture '{culture}' non trouvée. Consultez /cultures pour la liste complète.")
    try:
        datetime.strptime(date_plantation, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(400, "Format date invalide. Utilisez YYYY-MM-DD.")

    soil_type = SOIL_MAP.get(code, "Sols bruns calcaires")

    # Fetch real weather
    forecast_data, hist_data = await fetch_real_weather(lat, lon)
    forecast, hist, jours_sans = parse_forecast(forecast_data, hist_data)

    # If weather API failed, use simulated data
    if not forecast:
        jours_sans = 3
        today = datetime.now()
        forecast = [
            {"date": (today + timedelta(days=i)).strftime("%Y-%m-%d"),
             "jour": i, "temp_max": 24.0, "temp_min": 14.0, "temp_moy": 19.0,
             "precipitation": 0.0, "a_pluie": False, "code_meteo": 0,
             "description": "☀️ Ciel dégagé (données simulées)", "vent_kmh": 10.0}
            for i in range(1, 8)
        ]

    engine = RecommandationEngine(name, culture, date_plantation, forecast, hist, jours_sans, lat)
    stade, pourcentage, _, jours_plant = engine.calculer_stade()
    reco = engine.recommander(stade, soil_type)

    culture_info = CULTURES_DATA[culture]
    soil_info = SOIL_WATER_FACTOR.get(soil_type, {})

    return {
        "success": True,
        "wilaya": name, "wilaya_code": code,
        "lat": lat, "lon": lon,
        "culture": culture, "culture_ar": culture_info["ar"],
        "categorie_culture": culture_info["cat"],
        "soil_type": soil_type,
        "soil_retention": soil_info.get("retention", "?"),
        "date_plantation": date_plantation,
        "jours_depuis_plantation": jours_plant,
        "stade": stade,
        "progression_pct": pourcentage,
        "jours_sans_pluie": jours_sans,
        "forecast_7j": forecast,
        **reco,
    }

@app.get("/")
def root():
    return {
        "service": "🌾 API Agricole Algérienne v3.0",
        "wilayas": 58, "cultures": len(CULTURES_DATA),
        "meteo": "Open-Meteo (temps réel, gratuit)",
        "endpoints": {
            "GET /wilayas": "Liste des 58 wilayas",
            "GET /cultures": "Liste des 50+ cultures",
            "GET /weather?wilaya=Alger": "Météo réelle 7 jours",
            "GET /irrigation?wilaya=Blida&culture=Tomate&date_plantation=2026-03-01": "Recommandation complète"
        }
    }