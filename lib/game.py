def show_prompt(mud, id):
    mud.send_message(id, "")
    mud.send_message(id, "Entrez votre commande: ")


def ctxt(c, txt):
    return "\033["+str(c)+";1m"+txt+"\033[0m"
