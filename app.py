import streamlit as st
from dataclasses import asdict
import json
from openai import OpenAI
from main import Dipendente, suggest_benefits

# ─────────────────────────────────────────────────────────────────────────────
# Configurazione pagina
st.set_page_config(page_title="Welfare Advisor AI", layout="centered")
st.title("🌱 Welfare Advisor AI")

# ─────────────────────────────────────────────────────────────────────────────
# 1️⃣ Inizializzo il client OpenAI (v0.28+), legge da secrets.toml [openai]
client = OpenAI(api_key=st.secrets["openai"]["api_key"])

# 2️⃣ Carico la Knowledge-Base degli incentivi
with open("incentivi.json", encoding="utf-8") as f:
    INCENTIVI = json.load(f)

# ─────────────────────────────────────────────────────────────────────────────
# 3️⃣ Form unico per dati PMI + dati dipendente
with st.form("dati_completi"):
    st.header("🏢 Dati aziendali (PMI)")
    nome_hr        = st.text_input("Nome imprenditore / responsabile HR")
    nr_dipendenti  = st.number_input("Numero di dipendenti totali", min_value=1, step=1)
    budget_fiscale = st.number_input("Budget fiscale annuo (€)", min_value=0, step=1000)
    obiettivo      = st.selectbox(
        "Obiettivo principale",
        ["Massimizzare deducibilità spese", "Ottenere credito d'imposta", "Ridurre contributi"]
    )

    st.markdown("---")
    st.header("👤 Dati per suggerimento operativo")
    nome_dip      = st.text_input("Nome dipendente")
    età           = st.number_input("Età", min_value=18, max_value=75, step=1)
    ruolo_dip     = st.text_input("Ruolo aziendale")
    figli         = st.number_input("Numero di figli", min_value=0, step=1)
    preferenza    = st.selectbox("Preferenza benefit", ["Tempo libero", "Benefit economici"])
    distanza      = st.number_input("Distanza casa–ufficio (km)", min_value=0.0, step=0.1)
    stato_civile  = st.selectbox("Stato civile", ["single", "coppia", "altro"])
    settore       = st.selectbox("Reparto/settore", ["amministrazione", "produzione", "IT", "altro"])
    fascia_reddito= st.selectbox("Fascia di reddito", ["bassa", "media", "alta"])

    submitted = st.form_submit_button("Calcola Consulenza")

# ─────────────────────────────────────────────────────────────────────────────
if submitted:
    # ─── Debug: mostra i secrets caricati e ferma l’esecuzione ───
    st.write(">> DEBUG secrets:", st.secrets)
    st.stop()

    # — Benefit operativi
    dip       = Dipendente(
        nome=nome_dip, età=età, ruolo=ruolo_dip,
        figli=figli, preferenza=preferenza,
        distanza=distanza, stato_civile=stato_civile,
        settore=settore, fascia_reddito=fascia_reddito
    )
    pacchetto = suggest_benefits(dip)
    st.subheader(f"🎁 Pacchetto welfare consigliato per {dip.nome}")
    for b in pacchetto:
        st.write(f"- {b}")

    # — Incentivi normativi
    def suggest_incentives(data):
        consigli = []
        for inc in INCENTIVI:
            if data["nr_dipendenti"] > inc.get("max_dipendenti", float("inf")):
                continue
            di = inc["deducibilità_impresa"].lower()
            ti = inc["tassazione_dipendente"].lower()
            if data["obiettivo"].lower() not in di and data["obiettivo"].lower() not in ti:
                continue
            consigli.append(inc)
        return consigli

    data_pmi  = {
        "nr_dipendenti": nr_dipendenti,
        "budget_fiscale": budget_fiscale,
        "obiettivo": obiettivo
    }
    incentives= suggest_incentives(data_pmi)
    st.subheader("📑 Agevolazioni fiscali e contributive")
    for inc in incentives:
        st.markdown(
            f"**{inc['nome']}**  \n"
            f"Rif.: {inc['riferimento']}  \n"
            f"{inc['descrizione']}  \n"
            f"- Condizioni: {', '.join(inc['condizioni'])}  \n"
            f"- Deducibilità: {inc['deducibilità_impresa']}  \n"
            f"- Tassazione: {inc['tassazione_dipendente']}"
        )

    # — Prompt + chiamata GPT-4
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
        resp = client.chat.completions.create(
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

    # — Salvataggio output
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

