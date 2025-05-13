import streamlit as st
from dataclasses import asdict
import json
from main import Dipendente, suggest_benefits

# Configurazione pagina
st.set_page_config(page_title="Welfare Advisor AI", layout="centered")
st.title("🌱 Welfare Advisor AI")

# 1️⃣ Carico la Knowledge-Base degli incentivi
with open("incentivi.json", encoding="utf-8") as f:
    INCENTIVI = json.load(f)

# 2️⃣ Form unico per dati PMI + dati dipendente
with st.form("dati_completi"):
    # Sezione PMI
    st.header("Dati aziendali (PMI)")
    nome_hr = st.text_input("Nome imprenditore / responsabile HR")
    nr_dipendenti = st.number_input("Numero di dipendenti totali", min_value=1, step=1)
    budget_fiscale = st.number_input("Budget fiscale annuo disponibile (€)", min_value=0, step=1000)
    obiettivo = st.selectbox(
        "Obiettivo principale",
        ["Massimizzare deducibilità spese", "Ottenere credito d'imposta", "Ridurre contributi"]
    )

    st.markdown("---")
    # Sezione dipendente
    st.header("Dati per suggerimento operativo")
    nome_dip = st.text_input("Nome dipendente")
    età = st.number_input("Età", min_value=18, max_value=75, step=1)
    ruolo_dip = st.text_input("Ruolo aziendale (es. impiegato, quadro)")
    figli = st.number_input("Numero di figli", min_value=0, step=1)
    preferenza = st.selectbox("Preferenza benefit", ["Tempo libero", "Benefit economici"])
    distanza = st.number_input("Distanza casa–ufficio (km)", min_value=0.0, step=0.1)
    stato_civile = st.selectbox("Stato civile", ["single", "coppia", "altro"])
    settore = st.selectbox("Reparto/settore", ["amministrazione", "produzione", "IT", "altro"])
    fascia_reddito = st.selectbox("Fascia di reddito", ["bassa", "media", "alta"])

    submitted = st.form_submit_button("Calcola Consulenza")

# 3️⃣ Se invio, elaboro i suggerimenti
if submitted:
    # 3.1 Creo l’oggetto Dipendente per regole operative
    dip = Dipendente(
        nome=nome_dip,
        età=età,
        ruolo=ruolo_dip,
        figli=figli,
        preferenza=preferenza,
        distanza=distanza,
        stato_civile=stato_civile,
        settore=settore,
        fascia_reddito=fascia_reddito
    )

    # 3.2 Suggerimenti operativi (benefit)
    pacchetto = suggest_benefits(dip)
    st.subheader(f"🎁 Pacchetto welfare consigliato per {dip.nome}")
    for item in pacchetto:
        st.write(f"- {item}")

    # 3.3 Funzione per filtrare gli incentivi legislativi
    def suggest_incentives(data):
        consigli = []
        for inc in INCENTIVI:
            #  — filtro numero dipendenti (se specificato nel JSON)
            max_d = inc.get("max_dipendenti", float("inf"))
            if data["nr_dipendenti"] > max_d:
                continue
            #  — filtro obiettivo nella descrizione di deducibilità o tassazione
            ded_imp = inc["deducibilità_impresa"].lower()
            tass_dip = inc["tassazione_dipendente"].lower()
            if data["obiettivo"].lower() not in ded_imp and data["obiettivo"].lower() not in tass_dip:
                continue
            consigli.append(inc)
        return consigli

    # 3.4 Raggruppo i dati PMI in un dict
    data_pmi = {
        "nr_dipendenti": nr_dipendenti,
        "budget_fiscale": budget_fiscale,
        "obiettivo": obiettivo
    }

    # 3.5 Suggerimenti normativi (incentivi)
    incentives = suggest_incentives(data_pmi)
    st.subheader("📑 Agevolazioni fiscali e contributive")
    for inc in incentives:
        st.markdown(
            f"**{inc['nome']}**  \n"
            f"Rif.: {inc['riferimento']}  \n"
            f"{inc['descrizione']}  \n"
            f"- Condizioni: {', '.join(inc['condizioni'])}  \n"
            f"- Deducibilità impresa: {inc['deducibilità_impresa']}  \n"
            f"- Tassazione dipendente: {inc['tassazione_dipendente']}"
        )

    # 3.6 Salvo i risultati in JSON locale (opzionale)
    output = {
        "hr": nome_hr,
        **data_pmi,
        "dipendente": asdict(dip),
        "benefit_operativi": pacchetto,
        "incentivi_normativi": incentives
    }
    with open("output_consulenza.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)
    st.success("Risultati salvati in output_consulenza.json")

