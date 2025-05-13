import streamlit as st
from dataclasses import asdict
import json
import openai
from main import Dipendente, suggest_benefits

# Configurazione pagina
st.set_page_config(page_title="Welfare Advisor AI", layout="centered")
st.title("🌱 Welfare Advisor AI")

# Inizializzo OpenAI con la chiave da Streamlit Secrets
openai.api_key = st.secrets["openai_api_key"]

# 1️⃣ Carico la Knowledge-Base degli incentivi
with open("incentivi.json", encoding="utf-8") as f:
    INCENTIVI = json.load(f)

# 2️⃣ Form unico per dati PMI + dati dipendente
with st.form("dati_completi"):
    # Sezione PMI
    st.header("Dati aziendali (PMI)")
    nome_hr = st.text_input("Nome imprenditore / responsabile HR")
    nr_dipendenti = st.number_input("Numero di dipendenti totali", min_value=1, step=1)
    budget_fiscale = st.number_input(
        "Budget fiscale annuo disponibile (€)", min_value=0, step=1000)
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
    preferenza = st.selectbox(
        "Preferenza benefit", ["Tempo libero", "Benefit economici"]
    )
    distanza = st.number_input(
        "Distanza casa–ufficio (km)", min_value=0.0, step=0.1)
    stato_civile = st.selectbox(
        "Stato civile", ["single", "coppia", "altro"]
    )
    settore = st.selectbox(
        "Reparto/settore", ["amministrazione", "produzione", "IT", "altro"]
    )
    fascia_reddito = st.selectbox(
        "Fascia di reddito", ["bassa", "media", "alta"]
    )

    submitted = st.form_submit_button("Calcola Consulenza")

# 3️⃣ Se invio, elaboro i suggerimenti e genero la consulenza AI
if submitted:
    # Operativi: calcolo pacchetto benefit
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
    pacchetto = suggest_benefits(dip)
    st.subheader(f"🎁 Pacchetto welfare consigliato per {dip.nome}")
    for item in pacchetto:
        st.write(f"- {item}")

    # Normativi: filtro incentivi legislativi
    def suggest_incentives(data):
        consigli = []
        for inc in INCENTIVI:
            max_d = inc.get("max_dipendenti", float("inf"))
            if data["nr_dipendenti"] > max_d:
                continue
            ded_imp = inc["deducibilità_impresa"].lower()
            tass_dip = inc["tassazione_dipendente"].lower()
            if data["obiettivo"].lower() not in ded_imp and data["obiettivo"].lower() not in tass_dip:
                continue
            consigli.append(inc)
        return consigli

    data_pmi = {
        "nr_dipendenti": nr_dipendenti,
        "budget_fiscale": budget_fiscale,
        "obiettivo": obiettivo
    }
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

    # 3) Consulenza avanzata via GPT-4
    prompt = f"""
Sei un commercialista esperto di welfare aziendale.
L’azienda ha {nr_dipendenti} dipendenti e budget fiscale di €{budget_fiscale}.
Obiettivo: "{obiettivo}".
Elenca per ciascun incentivo:
1) Descrizione e funzionamento
2) Passi operativi concreti
3) Priorità e raccomandazioni.
Incentivi: {json.dumps(incentives, ensure_ascii=False, indent=2)}
"""
    with st.spinner("Generazione consulenza avanzata…"):
        resp = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Sei un consulente fiscale professionale."},
                {"role": "user",   "content": prompt}
            ],
            temperature=0.2,
            max_tokens=800
        )
    consulenza = resp.choices[0].message.content
    st.subheader("💬 Consulenza approfondita (AI)")
    st.write(consulenza)

    # 4) Salvataggio output completo
    output = {
        "hr": nome_hr,
        **data_pmi,
        "dipendente": asdict(dip),
        "benefit_operativi": pacchetto,
        "incentivi_normativi": incentives,
        "consulenza_ai": consulenza
    }
    with open("output_consulenza_ai.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)
    st.success("Consulenza salvata in output_consulenza_ai.json")
