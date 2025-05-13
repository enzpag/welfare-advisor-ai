def collect_employee_data():
    print("Benvenuto in Welfare Advisor AI\n")
    data = {}
    data['nome'] = input("Nome dipendente: ")
    data['età'] = int(input("Età: "))
    data['ruolo'] = input("Ruolo aziendale: ")
    data['figli'] = int(input("Numero di figli: "))
    data['preferenza'] = input("Preferisci più tempo libero o benefit economici? ")
    data['distanza'] = float(input("Distanza casa–ufficio (in km): "))
    data['stato_civile'] = input("Stato civile (single, coppia, altro): ")
    data['settore'] = input("Reparto/settore (es. amministrazione, produzione, IT): ")
    data['fascia_reddito'] = input("Fascia di reddito (bassa, media, alta): ")
    return data

def suggest_benefits(data):
    suggestions = []

    # Regole esistenti
    if data['figli'] > 0:
        suggestions.append("Contributo per asilo/nido")
    if data['preferenza'].lower().startswith("tempo"):
        suggestions.append("Smart working 2 giorni a settimana")
    else:
        suggestions.append("Buoni spesa / welfare card")

    # Nuove regole

    # 1. Distanza casa–ufficio
    if data['distanza'] >= 30:
        suggestions.append("Buoni trasporto o rimborso chilometrico")
    elif data['distanza'] >= 10:
        suggestions.append("Giorni extra di smart working")

    # 2. Stato civile
    if data['stato_civile'].lower() == "single":
        suggestions.append("Accesso a coworking vicino casa")
    else:
        suggestions.append("Voucher famiglia (attività ricreative)")

    # 3. Settore
    if data['settore'].lower() == "it":
        suggestions.append("Corso di formazione tecnologica")
    elif data['settore'].lower() == "produzione":
        suggestions.append("Pacchetto sicurezza e salute sul lavoro")

    # 4. Fascia di reddito
    if data['fascia_reddito'].lower() == "bassa":
        suggestions.append("Contributo una tantum per spese familiari")
    elif data['fascia_reddito'].lower() == "alta":
        suggestions.append("Piano previdenziale personalizzato")

    return suggestions

def main():
    dip = collect_employee_data()
    pacchetto = suggest_benefits(dip)
    print(f"\nPacchetto welfare consigliato per {dip['nome']}:")
    for b in pacchetto:
        print(" -", b)

if __name__ == "__main__":
    main()

