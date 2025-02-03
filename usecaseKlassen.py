import streamlit as st
import json
import numpy as np

# ---------------------------
# Klassen für Berechnungen
# ---------------------------

class Health:
    def __init__(self, vorname, nachname, gewicht, groesse, alter, geschlecht, aktivitaetsfaktor, trainingsintensitaet, bewegungsstunden):
        self.vorname = vorname
        self.nachname = nachname
        self.gewicht = gewicht
        self.groesse = groesse
        self.alter = alter
        self.geschlecht = geschlecht
        self.aktivitaetsfaktor = aktivitaetsfaktor
        self.trainingsintensitaet = trainingsintensitaet
        self.bewegungsstunden = bewegungsstunden

    def berechne_bmi(self):
        if self.groesse <= 0:
            return None
        return self.gewicht / (self.groesse ** 2)

    def taeglicher_wasserbedarf(self):
        wasser_ml = (30 * self.gewicht) + (350 * self.bewegungsstunden)
        return wasser_ml / 1000.0

    def berechne_proteinbedarf(self):
        if self.aktivitaetsfaktor <= 1.2:
            protein_pro_kg = 0.8
        elif self.aktivitaetsfaktor <= 1.5:
            protein_pro_kg = 1.2
        else:
            protein_pro_kg = 1.6
        return self.gewicht * protein_pro_kg

    def grundumsatz_berechnen(self):
        groesse_cm = self.groesse * 100
        if self.geschlecht == 'm':
            bmr = 10 * self.gewicht + 6.25 * groesse_cm - 5 * self.alter + 5
        else:
            bmr = 10 * self.gewicht + 6.25 * groesse_cm - 5 * self.alter - 161
        return bmr

    def gesamtumsatz_berechnen(self, bmr):
        return bmr * self.aktivitaetsfaktor

    def gewichtsstatus_bestimmen(self, bmi):
        if bmi is None:
            return "Unbekannt"
        if bmi < 18.5:
            return "Untergewicht"
        elif bmi < 25:
            return "Normalgewicht"
        elif bmi < 30:
            return "Übergewicht"
        else:
            return "Adipositas"

    def koerperfettanteil_schaetzen(self, bmi):
        geschlecht_int = 1 if self.geschlecht == 'm' else 0
        return 1.2 * bmi + 0.23 * self.alter - 10.8 * geschlecht_int - 5.4

    def herzfrequenzbereich_berechnen(self):
        max_puls = 220 - self.alter
        if self.trainingsintensitaet == 'leicht':
            return (0.5 * max_puls, 0.6 * max_puls)
        elif self.trainingsintensitaet == 'moderat':
            return (0.6 * max_puls, 0.75 * max_puls)
        else:
            return (0.75 * max_puls, 0.85 * max_puls)

    def empfohlene_erholungszeit(self):
        if self.trainingsintensitaet == 'leicht':
            return 24
        elif self.trainingsintensitaet == 'moderat':
            return 48
        else:
            return 72

    def makronaehrstoffverteilung(self, kalorienbedarf):
        kh_anteil = 0.5
        prot_anteil = 0.2
        fett_anteil = 0.3

        kh_kcal = kalorienbedarf * kh_anteil
        prot_kcal = kalorienbedarf * prot_anteil
        fett_kcal = kalorienbedarf * fett_anteil

        kh_g = kh_kcal / 4.0
        prot_g = prot_kcal / 4.0
        fett_g = fett_kcal / 9.0

        return kh_g, prot_g, fett_g

    def idealgewicht_schaetzen(self):
        groesse_cm = self.groesse * 100
        if self.geschlecht == 'm':
            ideal = (groesse_cm - 100) - ((groesse_cm - 100) * 0.1)
        else:
            ideal = (groesse_cm - 100) - ((groesse_cm - 100) * 0.15)
        return ideal

# ---------------------------
# Klassen für UI und Datenmanagement
# ---------------------------

class FitnessTrackerApp:
    def __init__(self):
        self.daten = []

    def lade_daten(self):
        json_datei = st.file_uploader("Optional: JSON-Datei mit Personendaten (Liste) hochladen", type=["json"])

        if json_datei is not None:
            daten = json.load(json_datei)
            if isinstance(daten, dict):
                daten = [daten]
            self.daten = daten
        else:
            self.erfasse_daten()

    def erfasse_daten(self):
        st.write("Keine JSON-Datei hochgeladen. Bitte manuelle Eingaben für eine Person vornehmen.")
        vorname = st.text_input("Vorname", value="")
        nachname = st.text_input("Nachname", value="")
        alter = st.number_input("Alter (Jahre)", value=30)
        gewicht = st.number_input("Gewicht (kg)", value=70.0)
        groesse = st.number_input("Größe (m)", value=1.75)
        geschlecht = st.selectbox("Geschlecht", options=["m", "w"])
        bewegungs_stunden = st.number_input("Körperliche Aktivität (h/Tag)", value=1.0)
        sitz_stunden = st.number_input("Sitzende Tätigkeit (h/Tag)", value=8.0)
        aktivitaetsfaktor = st.selectbox("Aktivitätsfaktor", [1.2, 1.5, 1.9])
        trainingsintensitaet = st.selectbox("Trainingsintensität", ["leicht", "moderat", "intensiv"])

        self.daten = [{
            "vorname": vorname,
            "nachname": nachname,
            "alter": alter,
            "gewicht": gewicht,
            "groesse": groesse,
            "geschlecht": geschlecht,
            "bewegungsStunden": bewegungs_stunden,
            "sitzStunden": sitz_stunden,
            "aktivitaetsFaktor": aktivitaetsfaktor,
            "trainingsIntensitaet": trainingsintensitaet
        }]

    def berechnungen_ausfuehren(self):
        if st.button("Berechnungen ausführen"):
            for idx, personendaten in enumerate(self.daten):
                st.subheader(f"{personendaten['vorname']} {personendaten['nachname']}")

                fitness = Health(
                    vorname=personendaten["vorname"],
                    nachname=personendaten["nachname"],
                    gewicht=personendaten["gewicht"],
                    groesse=personendaten["groesse"],
                    alter=personendaten["alter"],
                    geschlecht=personendaten["geschlecht"],
                    aktivitaetsfaktor=personendaten["aktivitaetsFaktor"],
                    trainingsintensitaet=personendaten["trainingsIntensitaet"],
                    bewegungsstunden=personendaten["bewegungsStunden"]
                )

                bmi = fitness.berechne_bmi()
                st.write(f"**BMI:** {bmi:.2f}")

                wasser = fitness.taeglicher_wasserbedarf()
                st.write(f"**Täglicher Wasserbedarf:** {wasser:.2f} L")

                protein = fitness.berechne_proteinbedarf()
                st.write(f"**Proteinbedarf:** {protein:.1f} g/Tag")

                bmr = fitness.grundumsatz_berechnen()
                st.write(f"**Grundumsatz (BMR):** {bmr:.0f} kcal/Tag")

                gesamt = fitness.gesamtumsatz_berechnen(bmr)
                st.write(f"**Gesamtumsatz:** {gesamt:.0f} kcal/Tag")

                status = fitness.gewichtsstatus_bestimmen(bmi)
                st.write(f"**Gewichtsstatus:** {status}")

                kfa = fitness.koerperfettanteil_schaetzen(bmi)
                st.write(f"**Körperfettanteil (Schätzung):** {kfa:.1f}%")

                hf_min, hf_max = fitness.herzfrequenzbereich_berechnen()
                st.write(f"**Herzfrequenzbereich ({personendaten['trainingsIntensitaet']}):** {hf_min:.0f} - {hf_max:.0f} bpm")

                erholung = fitness.empfohlene_erholungszeit()
                st.write(f"**Empfohlene Erholungszeit nach {personendaten['trainingsIntensitaet']} Training:** {erholung} Stunden")

                kh_g, p_g, f_g = fitness.makronaehrstoffverteilung(gesamt)
                st.write(f"**Makronährstoffverteilung** (bei {gesamt:.0f} kcal/Tag):")
                st.write(f"- Kohlenhydrate: {kh_g:.1f} g/Tag")
                st.write(f"- Proteine: {p_g:.1f} g/Tag")
                st.write(f"- Fette: {f_g:.1f} g/Tag")

                ideal = fitness.idealgewicht_schaetzen()
                st.write(f"**Idealgewicht:** {ideal:.1f} kg")

                st.write("---")

# ---------------------------
# Anwendung starten
# ---------------------------

class main:
    def main():
        st.title("Fitnesstracker")
        app = FitnessTrackerApp()
        app.lade_daten()
        app.berechnungen_ausfuehren()
    

    if __name__ == "__main__":
        main()