import streamlit as st
from dataclasses import asdict
import json
from jinja2 import Environment, FileSystemLoader
from main import Dipendente, suggest_benefits

# ─── Configurazione pagina ─────────────────────────────────────────────
st.set_page_config(page_title="Welfare Advisor AI", layout="centered")
st.title("🌱 Welfare Advisor AI")

# ─── 1️⃣ Inizializzo Jinja2 ────────────────────────────────────────────
#    Assicurati di avere dentro la cartella `templates/` un file `parere.txt`
env = Environment(
    loader=FileSystemLoader("templates"),
    trim_blocks=True,
    lstrip_blocks=True
)
template = env.get_template("parere.txt")

# ─── 2️⃣ Carico Knowledge-Base incentivi ───────────────────────────────
with open("incentivi.json", encoding="utf-8") as f:
    INCENTIVI = json.load(f)

# ─── 3️⃣ Form dati PMI + dipendente ───────────────────────────────────
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

    submitted = st.form_submit_button("Genera Report")

# ─── 4️⃣ Elaborazione ─────────────────────────────────────────────────
if submitted:
    # — a) Benefit operativi
    dip       = Dipendente(
        nome=nome_dip, età=età, ruolo=ruolo_dip,
        figli=figli, preferenza=preferenza,
        distanza=distanza, stato_civile=stato_civile,
        settore=settore, fascia_reddito=fascia_reddito
    )
    pacchetto = suggest_benefits(dip)
    st.subheader(f"🎁 Benefit operativi per {dip.nome}")
    for b in pacchetto:
        st.write(f"- {b}")

    # — b) Incentivi normativi
    def suggest_incentives(data):
        out = []
        for inc in INCENTIVI:
            if data["nr_dipendenti"] > inc.get("max_dipendenti", float("inf")):
                continue
            di = inc["deducibilità_impresa"].lower()
            ti = inc["tassazione_dipendente"].lower()
            if data["obiettivo"].lower() not in di and data["obiettivo"].lower() not in ti:
                continue
            out.append(inc)
        return out

    data_pmi   = {
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
            f"- Deducibilità: {inc['deducibilità_impresa']}  \n"
            f"- Tassazione: {inc['tassazione_dipendente']}"
        )

    # — c) Generazione report con Jinja2
    report = template.render(
        nome_hr=nome_hr,
        nr_dipendenti=nr_dipendenti,
        budget_fiscale=budget_fiscale,
        obiettivo=obiettivo,
        pacchetto=pacchetto,
        incentivi=incentives
    )
    st.subheader("📄 Report normativo dettagliato")
    st.text(report)

    # — d) Salvataggio report su file
    path = "report_welfare.txt"
    with open(path, "w", encoding="utf-8") as outf:
        outf.write(report)
    st.success(f"Report salvato come `{path}`")

    # — ➡️ aggiungo il pulsante di download
    with open(path, "rb") as f:
        data = f.read()
    st.download_button(
        label="⬇️ Scarica report normativo",
        data=data,
        file_name=path,
        mime="text/plain"
    )

