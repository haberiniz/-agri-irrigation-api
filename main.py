# main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
import numpy as np
import os

app = FastAPI(title="نظام الري الذكي الجزائري 🌾")

# ✅ السماح لـ Flutter بالاتصال من أي مكان
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================= DATA =================
WILAYA_COORDINATES = {
    "Adrar": {"lat": 27.8667, "lon": -0.2833}, "Chlef": {"lat": 36.1650, "lon": 1.3317},
    "Laghouat": {"lat": 33.8000, "lon": 2.8650}, "Oum El Bouaghi": {"lat": 35.8775, "lon": 7.1136},
    "Batna": {"lat": 35.5667, "lon": 6.1667}, "Bejaia": {"lat": 36.7500, "lon": 5.0833},
    "Biskra": {"lat": 34.8500, "lon": 5.7300}, "Bechar": {"lat": 31.6167, "lon": -2.2167},
    "Blida": {"lat": 36.4700, "lon": 2.8300}, "Bouira": {"lat": 36.3800, "lon": 3.9000},
    "Tamanrasset": {"lat": 22.7850, "lon": 5.5228}, "Tebessa": {"lat": 35.4000, "lon": 8.1167},
    "Tlemcen": {"lat": 34.8828, "lon": -1.3167}, "Tiaret": {"lat": 35.3667, "lon": 1.3167},
    "Tizi Ouzou": {"lat": 36.7200, "lon": 4.0500}, "Alger": {"lat": 36.7764, "lon": 3.0586},
    "Djelfa": {"lat": 34.6700, "lon": 3.2500}, "Jijel": {"lat": 36.8167, "lon": 5.7667},
    "Setif": {"lat": 36.1900, "lon": 5.4100}, "Saida": {"lat": 34.8300, "lon": 0.1500},
    "Skikda": {"lat": 36.8667, "lon": 6.9000}, "Sidi Bel Abbes": {"lat": 35.1900, "lon": -0.6400},
    "Annaba": {"lat": 36.9000, "lon": 7.7667}, "Guelma": {"lat": 36.4667, "lon": 7.4333},
    "Constantine": {"lat": 36.3650, "lon": 6.6147}, "Medea": {"lat": 36.2675, "lon": 2.7500},
    "Mostaganem": {"lat": 35.9300, "lon": 0.0900}, "M'Sila": {"lat": 35.7058, "lon": 4.5419},
    "Mascara": {"lat": 35.4000, "lon": 0.1333}, "Ouargla": {"lat": 31.9500, "lon": 5.3167},
    "Oran": {"lat": 35.6969, "lon": -0.6331}, "El Bayadh": {"lat": 33.6833, "lon": 1.0167},
    "Illizi": {"lat": 26.5000, "lon": 8.4167}, "Bordj Bou Arreridj": {"lat": 36.0700, "lon": 4.7600},
    "Boumerdes": {"lat": 36.7600, "lon": 3.4800}, "El Tarf": {"lat": 36.7667, "lon": 8.3167},
    "Tindouf": {"lat": 27.6667, "lon": -8.1333}, "Tissemsilt": {"lat": 35.6000, "lon": 1.8167},
    "El Oued": {"lat": 33.3667, "lon": 6.8667}, "Khenchela": {"lat": 35.4333, "lon": 7.1333},
    "Souk Ahras": {"lat": 36.2833, "lon": 7.9500}, "Tipaza": {"lat": 36.5900, "lon": 2.4400},
    "Mila": {"lat": 36.4500, "lon": 6.2667}, "Ain Defla": {"lat": 36.2600, "lon": 1.9700},
    "Naama": {"lat": 33.2667, "lon": -0.3167}, "Ain Temouchent": {"lat": 35.3000, "lon": -1.1333},
    "Ghardaia": {"lat": 32.4833, "lon": 3.6667}, "Relizane": {"lat": 35.7400, "lon": 0.5500},
    "Timimoun": {"lat": 29.2667, "lon": 0.2333}, "Bordj Badji Mokhtar": {"lat": 21.3833, "lon": 0.9500},
    "Ouled Djellal": {"lat": 34.4333, "lon": 5.0667}, "Beni Abbes": {"lat": 30.1167, "lon": -2.1667},
    "In Salah": {"lat": 27.2000, "lon": 2.4833}, "In Guezzam": {"lat": 19.5667, "lon": 5.7667},
    "Touggourt": {"lat": 33.1000, "lon": 6.0667}, "Djanet": {"lat": 24.5500, "lon": 9.4833},
    "El M'Ghair": {"lat": 33.9500, "lon": 5.9167}, "El Menia": {"lat": 30.5833, "lon": 2.8833}
}

WILAYA_SOIL_MAPPING = {v: k for k, v in WILAYA_COORDINATES.items()} # اختصار، الرمز الحقيقي تحت
SOIL_MAP = {
    "Adrar": "Sols sableux (Erg)", "Chlef": "Sols alluviaux", "Laghouat": "Sols sableux (Erg)",
    "Oum El Bouaghi": "Vertisols", "Batna": "Sols peu evolues d erosion", "Bejaia": "Sols bruns calcaires",
    "Biskra": "Sols sableux (Erg)", "Bechar": "Sols sableux (Erg)", "Blida": "Sols alluviaux",
    "Bouira": "Sols bruns calcaires", "Tamanrasset": "Sols mineraux bruts (Reg)", "Tebessa": "Sols bruns calcaires",
    "Tlemcen": "Sols bruns calcaires", "Tiaret": "Sols bruns calcaires", "Tizi Ouzou": "Sols peu evolues d erosion",
    "Alger": "Sols alluviaux", "Djelfa": "Sols bruns calcaires", "Jijel": "Sols bruns calcaires",
    "Setif": "Sols bruns calcaires", "Saida": "Sols bruns calcaires", "Skikda": "Sols bruns calcaires",
    "Sidi Bel Abbes": "Sols bruns calcaires", "Annaba": "Sols alluviaux", "Guelma": "Vertisols",
    "Constantine": "Vertisols", "Medea": "Sols bruns calcaires", "Mostaganem": "Sols bruns calcaires",
    "M'Sila": "Sols bruns calcaires", "Mascara": "Sols bruns calcaires", "Ouargla": "Sols sableux (Erg)",
    "Oran": "Sols bruns calcaires", "El Bayadh": "Sols bruns calcaires", "Illizi": "Sols mineraux bruts (Reg)",
    "Bordj Bou Arreridj": "Sols bruns calcaires", "Boumerdes": "Sols bruns calcaires", "El Tarf": "Sols hydromorphes (Oasis)",
    "Tindouf": "Sols mineraux bruts (Reg)", "Tissemsilt": "Sols bruns calcaires", "El Oued": "Sols sableux (Erg)",
    "Khenchela": "Sols bruns calcaires", "Souk Ahras": "Sols bruns calcaires", "Tipaza": "Sols alluviaux",
    "Mila": "Vertisols", "Ain Defla": "Sols alluviaux", "Naama": "Sols bruns calcaires",
    "Ain Temouchent": "Sols bruns calcaires", "Ghardaia": "Sols hydromorphes (Oasis)", "Relizane": "Sols bruns calcaires",
    "Timimoun": "Sols sableux (Erg)", "Bordj Badji Mokhtar": "Sols mineraux bruts (Reg)", "Ouled Djellal": "Sols sableux (Erg)",
    "Beni Abbes": "Sols sableux (Erg)", "In Salah": "Sols mineraux bruts (Reg)", "In Guezzam": "Sols mineraux bruts (Reg)",
    "Touggourt": "Sols hydromorphes (Oasis)", "Djanet": "Sols mineraux bruts (Reg)", "El M'Ghair": "Sols hydromorphes (Oasis)",
    "El Menia": "Sols sableux (Erg)"
}

CULTURES_DATA = {
    "Tomate": {"kc_ini": 0.6, "kc_mid": 1.15, "kc_end": 0.8, "zr": 0.7, "cycle_jours": 120,
               "stades": {"Initial": (0, 30), "Developpement": (30, 70), "Milieu": (70, 100), "Fin": (100, 120)}, "besoin_base": 6},
    "Ble dur": {"kc_ini": 0.4, "kc_mid": 1.15, "kc_end": 0.4, "zr": 1.0, "cycle_jours": 180,
                "stades": {"Initial": (0, 40), "Developpement": (40, 100), "Milieu": (100, 150), "Fin": (150, 180)}, "besoin_base": 5},
    "Orge": {"kc_ini": 0.35, "kc_mid": 1.10, "kc_end": 0.35, "zr": 0.9, "cycle_jours": 150,
             "stades": {"Initial": (0, 30), "Developpement": (30, 80), "Milieu": (80, 120), "Fin": (120, 150)}, "besoin_base": 4.5},
    "Pomme de terre": {"kc_ini": 0.5, "kc_mid": 1.15, "kc_end": 0.75, "zr": 0.6, "cycle_jours": 100,
                       "stades": {"Initial": (0, 25), "Developpement": (25, 60), "Milieu": (60, 85), "Fin": (85, 100)}, "besoin_base": 5.5},
    "Olivier": {"kc_ini": 0.65, "kc_mid": 0.70, "kc_end": 0.65, "zr": 1.2, "cycle_jours": 365,
                "stades": {"Initial": (0, 90), "Developpement": (90, 180), "Milieu": (180, 270), "Fin": (270, 365)}, "besoin_base": 4},
    "Palmier dattier": {"kc_ini": 0.80, "kc_mid": 1.05, "kc_end": 0.85, "zr": 1.5, "cycle_jours": 365,
                        "stades": {"Initial": (0, 90), "Developpement": (90, 200), "Milieu": (200, 300), "Fin": (300, 365)}, "besoin_base": 8},
    "Mais": {"kc_ini": 0.3, "kc_mid": 1.20, "kc_end": 0.6, "zr": 0.9, "cycle_jours": 130,
             "stades": {"Initial": (0, 30), "Developpement": (30, 70), "Milieu": (70, 110), "Fin": (110, 130)}, "besoin_base": 6.5}
}

# ================= CLASSES =================
class LSTMWeatherPredictor:
    def __init__(self, wilaya):
        self.wilaya = wilaya
        self.historique = []
        self.previsions = []

    def get_climat_data(self):
        coords = WILAYA_COORDINATES.get(self.wilaya, {"lat": 36.7764, "lon": 3.0586})
        lat = coords["lat"]
        if lat > 34:
            return {"temp": [12,12,14,16,19,23,26,27,25,21,16,13], "pluie": [90,80,70,60,45,15,5,10,35,70,90,100], "jours_pluie": [13,11,10,8,6,2,1,2,4,7,11,13]}
        elif lat > 32:
            return {"temp": [8,9,11,13,17,22,26,26,22,17,12,9], "pluie": [70,65,60,55,45,20,10,15,35,50,65,75], "jours_pluie": [12,11,10,9,7,4,2,3,6,8,10,12]}
        else:
            return {"temp": [12,14,18,22,27,33,36,35,30,24,17,13], "pluie": [15,10,15,10,5,2,1,5,10,15,20,15], "jours_pluie": [3,2,3,2,2,1,0,1,2,3,3,3]}

    def generer_historique(self, jours=30):
        climat = self.get_climat_data()
        today = datetime.now()
        self.historique = []
        for i in range(jours, -1, -1):
            date = today - timedelta(days=i)
            mois = date.month - 1
            temp_base = climat['temp'][mois]
            pluie_base = climat['pluie'][mois] / max(1, climat['jours_pluie'][mois])
            temp = temp_base + np.random.normal(0, 2)
            pluie = np.random.exponential(pluie_base) if np.random.random() < climat['jours_pluie'][mois]/30 else 0
            self.historique.append({'date': date, 'temperature': round(temp, 1), 'precipitation': round(pluie, 1)})
        return self.historique

    def prevoir_meteo(self, jours=7):
        climat = self.get_climat_data()
        today = datetime.now()
        self.previsions = []
        for i in range(1, jours+1):
            date = today + timedelta(days=i)
            mois = date.month - 1
            temp_base = climat['temp'][mois]
            pluie_base = climat['pluie'][mois] / max(1, climat['jours_pluie'][mois])
            temp = temp_base + np.random.normal(0, 1.5)
            pluie = np.random.exponential(pluie_base) if np.random.random() < climat['jours_pluie'][mois]/30 else 0
            self.previsions.append({'date': date.strftime('%d/%m'), 'jour': i, 'temperature': round(temp, 1), 'precipitation': round(pluie, 1), 'a_pluie': pluie > 0.5})
        return self.previsions

    def jours_sans_pluie_consecutifs(self):
        if not self.historique: self.generer_historique()
        jours_sans = 0
        for jour in reversed(self.historique):
            if jour['precipitation'] < 0.5: jours_sans += 1
            else: break
        return jours_sans

class ArrosageIntelligent:
    def __init__(self, wilaya, culture, date_plantation, soil_type):
        self.wilaya = wilaya
        self.culture = culture
        self.date_plantation = date_plantation
        self.soil_type = soil_type
        self.meteo = LSTMWeatherPredictor(wilaya)
        self.culture_data = CULTURES_DATA.get(culture, CULTURES_DATA["Tomate"])

    def calculer_stade(self):
        today = datetime.now()
        jours = (today - self.date_plantation).days
        if jours < 0: return "Non plante", 0, self.culture_data['cycle_jours'], jours
        for stade, (debut, fin) in self.culture_data['stades'].items():
            if debut <= jours <= fin:
                pourcentage = int((jours - debut) / (fin - debut) * 100) if fin > debut else 0
                return stade, pourcentage, fin - debut, jours
        if jours > self.culture_data['cycle_jours']: return "Cycle termine", 100, 0, jours
        return "Inconnu", 0, 0, jours

    def calculer_quantite_eau(self, stade, jours_sans_pluie):
        besoin_base = self.culture_data['besoin_base']
        coeff_stade = {'Initial': 0.5, 'Developpement': 0.8, 'Milieu': 1.2, 'Fin': 0.6, 'Cycle termine': 0.3, 'Non plante': 0}
        coeff = coeff_stade.get(stade, 0.7)
        stress = min(1.3, 1 + (jours_sans_pluie / 25))
        facteur_sol = {"Sols sableux (Erg)": 1.3, "Sols alluviaux": 0.9, "Sols bruns calcaires": 1.0, "Vertisols": 0.8, "Sols peu evolues d erosion": 1.1, "Sols hydromorphes (Oasis)": 0.85}
        facteur = facteur_sol.get(self.soil_type, 1.0)
        quantite_base = besoin_base * coeff * stress * facteur

        pluie_prochaine = 0
        jours_avant_pluie = 999
        for prev in self.meteo.previsions[:7]:
            if prev['a_pluie'] and prev['precipitation'] > 1:
                pluie_prochaine = prev['precipitation']
                jours_avant_pluie = prev['jour']
                break

        quantite, niveau, raison = quantite_base, "🔴 FORTE", "Aucune pluie significative prevue dans les 7 jours"
        if pluie_prochaine > 0 and jours_avant_pluie <= 2:
            if pluie_prochaine >= 4: quantite, niveau, raison = 0, "🟢 AUCUNE", f"Pluie imminente de {pluie_prochaine} mm"
            elif pluie_prochaine >= 2: quantite, niveau, raison = max(0, quantite_base*0.2), "🟡 TRES LEGERE", f"Pluie moderee ({pluie_prochaine} mm) dans {jours_avant_pluie} jours"
            else: quantite, niveau, raison = quantite_base*0.4, "🟡 LEGERE", f"Faible pluie ({pluie_prochaine} mm) dans {jours_avant_pluie} jours"
        elif pluie_prochaine > 0 and jours_avant_pluie <= 4:
            if pluie_prochaine >= 5: quantite, niveau, raison = max(0, quantite_base*0.3), "🟡 LEGERE", f"Forte pluie ({pluie_prochaine} mm) dans {jours_avant_pluie} jours"
            elif pluie_prochaine >= 3: quantite, niveau, raison = max(0, quantite_base*0.5), "🟡 MODEREE", f"Pluie de {pluie_prochaine} mm dans {jours_avant_pluie} jours"
            else: quantite, niveau, raison = quantite_base*0.7, "🟠 NORMALE LEGERE", f"Faible pluie ({pluie_prochaine} mm) dans {jours_avant_pluie} jours"
        elif pluie_prochaine > 0 and jours_avant_pluie <= 7:
            quantite, niveau, raison = quantite_base*0.8, "🟠 NORMALE", f"Pluie prevue dans {jours_avant_pluie} jours"

        return max(0, round(quantite, 1)), niveau, raison

    def analyser_besoin(self):
        self.meteo.generer_historique(30)
        self.meteo.prevoir_meteo(14)
        jours_sans = self.meteo.jours_sans_pluie_consecutifs()
        stade, pourcentage, _, jours_plant = self.calculer_stade()
        quantite, niveau, raison = self.calculer_quantite_eau(stade, jours_sans)
        return {
            'stade': stade, 'progression_pct': pourcentage, 'jours_sans_pluie': jours_sans,
            'quantite_eau': quantite, 'niveau_urgence': niveau, 'raison': raison,
            'previsions_7j': self.meteo.previsions[:7]
        }

# ================= API ENDPOINTS =================
@app.get("/irrigation")
def get_irrigation(wilaya: str, culture: str, date_plantation: str):
    if wilaya not in SOIL_MAP: raise HTTPException(400, "Wilaya غير موجودة في القائمة")
    if culture not in CULTURES_DATA: raise HTTPException(400, "Culture غير موجودة")
    
    try:
        date_obj = datetime.strptime(date_plantation, "%Y-%m-%d")
        soil = SOIL_MAP[wilaya]
        system = ArrosageIntelligent(wilaya, culture, date_obj, soil)
        return system.analyser_besoin()
    except Exception as e:
        raise HTTPException(400, f"خطأ في المعالجة: {str(e)}")

@app.get("/")
def root():
    return {"message": "🌾 API نظام الري الذكي الجزائري يعمل بنجاح"}