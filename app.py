import streamlit as st
from dataclasses import asdict
import json
from openai import OpenAI        # client v0.28+
from main import Dipendente, suggest_benefits

# config pagina
st.set_page_config(page_title="Welfare Advisor AI", layout="centered")

# — 1️⃣ Inizializzo il client OpenAI (v0.28+)
client = OpenAI(api_key=st.secrets["openai"]["api_key"])

# — 2️⃣ Carico incentivi
with open("incentivi.json", encoding="utf-8") as f:
    INCENTIVI = json.load(f)

# — 3️⃣ Form PMI + dipendente
with st.form("dati_completi"):
    # ... qui tutti i tuoi campi ...
    submitted = st.form_submit_button("Calcola Consulenza")

if submitted:
    # — calcolo benefit operativi
    dip = Dipendente( ... )
    pacchetto = suggest_benefits(dip)
    # ... visualizzo pacchetto ...

    # — filtro incentivi normativi
    def suggest_incentives(data): ...
    incentives = suggest_incentives({ ... })

    # — 4️⃣ Chiamata a GPT-4
    prompt = f"""Sei un commercialista ... Incentivi: {json.dumps(incentives, ...)}"""
    with st.spinner("Generazione…"):
        resp = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role":"system","content":"Sei un consulente fiscale."},
                {"role":"user","content":prompt}
            ],
            temperature=0.2,
            max_tokens=800
        )
    consulenza = resp.choices[0].message.content
    st.write(consulenza)

