def show_prompt(mud, id):
    mud.send_message(id, "")
    mud.send_message(id, "Entrez votre commande ['m' pour voir le menu]: ")


def ctxt(c, txt):
    return "\033["+str(c)+";1m"+txt+"\033[0m"

def txt(mud, id, txt):
    mud.send_message(id, txt+"\r\n")