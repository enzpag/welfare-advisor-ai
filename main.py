from dataclasses import dataclass
import json

# Definizione del dataclass per il dipendente
@dataclass
class Dipendente:
    nome: str
    età: int
    ruolo: str
    figli: int
    preferenza: str
    distanza: float  # in km
    stato_civile: str
    settore: str
    fascia_reddito: str

def collect_employee_data() -> Dipendente:
    """Raccoglie i dati del dipendente e restituisce un’istanza di Dipendente."""
    print("Benvenuto in Welfare Advisor AI\n")
    nome = input("Nome dipendente: ")
    età = int(input("Età: "))
    ruolo = input("Ruolo aziendale: ")
    figli = int(input("Numero di figli: "))
    preferenza = input("Preferisci più tempo libero o benefit economici? ")
    distanza = float(input("Distanza casa–ufficio (in km): "))
    stato_civile = input("Stato civile (single, coppia, altro): ")
    settore = input("Reparto/settore (es. amministrazione, produzione, IT): ")
    fascia_reddito = input("Fascia di reddito (bassa, media, alta): ")
    return Dipendente(nome, età, ruolo, figli, preferenza, distanza, stato_civile, settore, fascia_reddito)

def suggest_benefits(d: Dipendente) -> list[str]:
    """Applica le regole e restituisce la lista di benefit consigliati."""
    suggestions: list[str] = []

    # Regole di base
    if d.figli > 0:
        suggestions.append("Contributo per asilo/nido")
    if d.preferenza.lower().startswith("tempo"):
        suggestions.append("Smart working 2 giorni a settimana")
    else:
        suggestions.append("Buoni spesa / welfare card")

    # 1. Distanza casa–ufficio
    if d.distanza >= 30:
        suggestions.append("Buoni trasporto o rimborso chilometrico")
    elif d.distanza >= 10:
        suggestions.append("Giorni extra di smart working")

    # 2. Stato civile
    if d.stato_civile.lower() == "single":
        suggestions.append("Accesso a coworking vicino casa")
    else:
        suggestions.append("Voucher famiglia (attività ricreative)")

    # 3. Settore
    settore = d.settore.lower()
    if settore == "it":
        suggestions.append("Corso di formazione tecnologica")
    elif settore == "produzione":
        suggestions.append("Pacchetto sicurezza e salute sul lavoro")

    # 4. Fascia di reddito
    fascia = d.fascia_reddito.lower()
    if fascia == "bassa":
        suggestions.append("Contributo una tantum per spese familiari")
    elif fascia == "alta":
        suggestions.append("Piano previdenziale personalizzato")

    return suggestions

def save_to_file(d: Dipendente, suggestions: list[str]) -> None:
    """Salva i dati e i suggerimenti in un file JSON."""
    output = {**d.__dict__, "suggerimenti": suggestions}
    with open("output.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

def main():
    dip = collect_employee_data()
    pacchetto = suggest_benefits(dip)
    print(f"\nPacchetto welfare consigliato per {dip.nome}:")
    for b in pacchetto:
        print(" -", b)
    save_to_file(dip, pacchetto)
    print("\n[✓] I risultati sono stati salvati in output.json")

if __name__ == "__main__":
    main()



