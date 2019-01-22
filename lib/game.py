def background(mud, id):
    mud.send_message(id, "\033[=3h")
    mud.send_message(id, "\033[0;0H"+"-"*80)

    for i in range(2,24):
        mud.send_message(id, "\033["+str(i)+";0H|")
        mud.send_message(id, "\033["+str(i)+";80H|")

    mud.send_message(id, "\033[24;0H"+"-"*80)


def show_prompt(mud, id):
    mud.send_message(id, "\033[24;0H"+"-"*80)
    mud.send_message(id, "\033[21;0H"+"-"*80)
    mud.send_message(id, "\033[22;2H"+" "*78)
    mud.send_message(id, "\033[22;2HEntrez votre commande: ")


def pos(l,c):
    return "\033["+str(l)+";"+str(c)+"H"


def con(c):
    return "\033["+str(c)+";1m"


def cof():
    return "\033[0m"


def ctxt(c, txt):
    return "\033["+str(c)+";1m"+txt+"\033[0m"


def txt(texte, new):
    texte.append(new)

    if len(texte) == 20:
        texte.pop(0)

    return texte


def refresh(mud, id, texte):
    background(mud, id)

    for i in range(2, 21):
        mud.send_message(id, "\033["+str(i)+";2H"+" "*78)

    for i in range(0, len(texte)):
        mud.send_message(id, "\033[" + str(i+2) + ";2H" + texte[i])

    show_prompt(mud, id)
