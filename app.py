import streamlit as st
from dataclasses import asdict
import json
from main import Dipendente, collect_employee_data, suggest_benefits

st.set_page_config(page_title="Welfare Advisor AI", layout="centered")
st.title("🌱 Welfare Advisor AI")

# 1. Raccogli i dati via form
with st.form("dati_dipendente"):
    nome = st.text_input("Nome dipendente")
    età = st.number_input("Età", min_value=18, max_value=75, step=1)
    ruolo = st.text_input("Ruolo aziendale")
    figli = st.number_input("Numero di figli", min_value=0, step=1)
    preferenza = st.selectbox("Preferisci…", ["Tempo libero", "Benefit economici"])
    distanza = st.number_input("Distanza casa–ufficio (km)", min_value=0.0, step=0.1)
    stato_civile = st.selectbox("Stato civile", ["single", "coppia", "altro"])
    settore = st.selectbox("Reparto/settore", ["amministrazione", "produzione", "IT", "altro"])
    fascia_reddito = st.selectbox("Fascia di reddito", ["bassa", "media", "alta"])
    submitted = st.form_submit_button("Calcola Pacchetto")

if submitted:
    # 2. Crea istanza Dipendente e genera suggerimenti
    dip = Dipendente(nome, età, ruolo, figli, preferenza, distanza, stato_civile, settore, fascia_reddito)
    pacchetto = suggest_benefits(dip)

    # 3. Mostra i risultati
    st.subheader(f"Pacchetto welfare consigliato per {dip.nome}")
    for item in pacchetto:
        st.write(f"- {item}")

    # 4. Salva su JSON
    output = asdict(dip)
    output["suggerimenti"] = pacchetto
    with open("output.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)
    st.success("Risultati salvati in output.json")
