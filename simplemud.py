import time
import sqlite3
import random

# import the MUD server class
from mudserver import MudServer
from lib.bd import *
from lib.game import *

conn = sqlite3.connect('cendrelune.db')

# structure defining the rooms in the game. Try adding more rooms to the game!
rooms = {
    "Tavern": {
        "description": "You're in a cozy tavern warmed by an open fire.",
        "exits": {"outside": "Outside"},
    },
    "Outside": {
        "description": "You're standing outside a tavern. It's raining.",
        "exits": {"inside": "Tavern"},
    }
}

# liste des joueurs connectés
players = {}

# start the server
mud = MudServer()

# main game loop. We loop forever (i.e. until the program is terminated)
while True:

    # pause for 1/5 of a second on each loop, so that we don't constantly
    # use 100% CPU time
    time.sleep(0.2)

    # 'update' must be called in the loop to keep the game running and give
    # us up-to-date information
    mud.update()

    # test d'event par interval
    #if random.randint(0, 10) > 8:
    #   for pid, pl in players.items():
    #        if players[pid]['connexion'] == 1:
    #            mud.send_message(pid, "\nIl pleut...")

    # go through any newly connected players
    for id in mud.get_new_players():

        # add the new player to the dictionary, noting that they've not been
        # named yet.
        # The dictionary key is the player's id number. We set their room to
        # None initially until they have entered a name
        # Try adding more player stats - level, gold, inventory, etc
        players[id] = {
            "name": None,
            "password": None,
            "room": None,
            "connexion": 0
        }

        # send the new player a prompt for their name
        background(mud, id)
        refresh_content(mud,id)

        mud.send_message(id, pos(2, 2)+ctxt(37, "---------- CENDRELUNE le retour ----------"))
        mud.send_message(id, pos(4, 2)+"Pour creer un nouveau personnages: "+ctxt(37, "creer")+" <nom> <motdepasse>")
        mud.send_message(id, pos(5, 2)+"Pour jouer avec un personnage existant: "+ctxt(37, "connexion")+" <nom> <motdepasse>")

        show_prompt(mud, id)

    # go through any recently disconnected players
    for id in mud.get_disconnected_players():

        # on verifie si le joueur est bien dans la liste des connectés
        # sinon on laisse tomber
        if id not in players:
            continue

        # on parse tous les joueurs connectés
        for pid, pl in players.items():
            if pid != id:
                # envoie d'un message a chacun, sauf au joueur qui quitte
                txt = "{} a quitte le jeu.".format(players[id]["name"])
                mud.send_message(pid, pos(23,2) + ctxt(31, txt))

        # on enleve le joueur de la liste des connectés
        del(players[id])

    # go through any new commands sent from players
    for id, command, params in mud.get_commands():

        # if for any reason the player isn't in the player map, skip them and
        # move on to the next one
        if id not in players:
            continue

        # each of the possible commands is handled below. Try adding new
        # commands to the game!

        # 'create' command
        elif command == 'creer' and players[id]["connexion"] == 0:

            # creation d'un nouveau joueur
            #
            # on doit verifier si le compte existe deja en BD (= le nom existe deja)
            # s'il n'existe pas on le crée
            # sinon on refuse et on demande de changer le nom au joueur
            theParams = params.split()

            playerExist = player_exist(conn, theParams[0])

            if playerExist == 1:
                # ce nom existe deja dans la BD !
                refresh_content(mud, id)

                mud.send_message(id, "\033[2;2HCe nom de joueur existe deja dans notre base !")
                mud.send_message(id, "\033[4;2HMerci d'en choisir un autre ou de vous connecter en tapant la commande :")
                mud.send_message(id, "\033[5;2H\033[1mconnect \033[0m "+theParams[0]+" <motdepasse>\n")

                show_prompt(mud, id)
            else:
                # on crée le nouveau joueur
                player_add(conn, theParams)
                players[id]["connexion"] = 1

                # on l'enregistre dans la table temporaraire des joueurs en ligne
                players[id]["name"] = theParams[0]
                players[id]["password"] = theParams[1]

                # on lui affiche un message de bienvenue
                refresh_content(mud, id)

                mud.send_message(id, "\033[2;2HNouveau commpte créé !")
                mud.send_message(id, "\033[4;2HBienvenue dans Cendrelune, {}.\n".format(players[id]["name"]))
                mud.send_message(id, "\033[5;2HEntrez 'help' pour voir la liste des commandes. Bon jeu !")

                show_prompt(mud, id)

                # on le place dans la zone de début du jeu
                # on lui affiche la description de la zone
                players[id]["room"] = "Tavern"
                #mud.send_message(id, get_zone_description(conn, "Tavern"))

                # on prévient les autres joueurs connectés qu'il vient d'arriver
                for pid, pl in players.items():
                    if pid != id:
                        # send each player a message to tell them about the new player
                        mud.send_message(pid, "\033[23;2H\033[31;1m{} vient de se connecter.\033[0m".format( players[id]["name"]))

        # 'aide' command
        elif command == "aide":

            refresh_content(mud, id)

            mud.send_message(id, pos(2, 2) +"Commandes :")
            mud.send_message(id, pos(4, 2) +ctxt(37, "reg                    ")+"- regarder autour de vous")
            mud.send_message(id, pos(5, 2) +ctxt(37, "dire <message>         ")+"- dit un texte aux joueurs presents dans la zone")
            mud.send_message(id, pos(6, 2) +ctxt(37, "aller <sortie>         ")+"- se deplace vers une autre zone")
            mud.send_message(id, pos(6, 2) +ctxt(37, "donne <objet> <joueur> ")+"- donne un objet de votre inventaire a un joueur")
            mud.send_message(id, pos(7, 2) +ctxt(37, "prendre <objet>        ")+"- prends un objet et le met dans l'inventaire")
            mud.send_message(id, pos(8, 2) +ctxt(37, "perso                  ")+"- affiche la feuille de personnage")
            mud.send_message(id, pos(9, 2) +ctxt(37, "magie                  ")+"- affiche vos sorts")
            mud.send_message(id, pos(10, 2)+ctxt(37, "combat                 ")+"- passe en mode combat")
            mud.send_message(id, pos(11, 2)+ctxt(37, "fuir                   ")+"- fuit le combat")

        # 'say' command
        elif command == "dire" and players[id]["connexion"] == 1:

            # go through every player in the game
            for pid, pl in players.items():
                # if they're in the same room as the player
                if players[pid]["room"] == players[id]["room"]:
                    # send them a message telling them what the player said
                    mud.send_message(pid, "{} dit: {}".format(
                                                players[id]["name"], params))

        # 'look' command
        elif command == "regarder" or command == 'reg':

            if players[id]["connexion"] == 1:
                # store the player's current room
                rm = rooms[players[id]["room"]]

                # send the player back the description of their current room
                mud.send_message(id, get_zone_description(conn, players[id]["room"]))

                playershere = []
                # go through every player in the game
                for pid, pl in players.items():
                    # if they're in the same room as the player
                    if players[pid]["room"] == players[id]["room"]:
                        # ... and they have a name to be shown
                        if players[pid]["name"] is not None:
                            # add their name to the list
                            playershere.append(players[pid]["name"])

                # send player a message containing the list of players in the room
                mud.send_message(id, "Joueurs presents: {}".format(", ".join(playershere)))

                # send player a message containing the list of exits from this room
                mud.send_message(id, "Sorties visibles: {}".format(", ".join(rm["exits"])))

        # 'go' command
        elif command == "go" and players[id]["connexion"] == 1:

            # store the exit name
            ex = params.lower()

            # store the player's current room
            rm = rooms[players[id]["room"]]

            # if the specified exit is found in the room's exits list
            if ex in rm["exits"]:

                # go through all the players in the game
                for pid, pl in players.items():
                    # if player is in the same room and isn't the player
                    # sending the command
                    if players[pid]["room"] == players[id]["room"] and pid != id:
                        # send them a message telling them that the player
                        # left the room
                        mud.send_message(pid, "{} left via exit '{}'".format(players[id]["name"], ex))

                # update the player's current room to the one the exit leads to
                players[id]["room"] = rm["exits"][ex]
                rm = rooms[players[id]["room"]]

                # go through all the players in the game
                for pid, pl in players.items():
                    # if player is in the same (new) room and isn't the player
                    # sending the command
                    if players[pid]["room"] == players[id]["room"] and pid != id:
                        # send them a message telling them that the player
                        # entered the room
                        mud.send_message(pid, "{} arrived via exit '{}'".format(players[id]["name"], ex))

                # send the player a message telling them where they are now
                mud.send_message(id, "Vous arrivez a: '{}'".format(players[id]["room"]))

            # the specified exit wasn't found in the current room
            else:
                # send back an 'unknown exit' message
                mud.send_message(id, "Sortie inconnue: '{}'".format(ex))

        # some other, unrecognised command
        else:
            # send back an 'unknown command' message
            mud.send_message(id, pos(23, 2)+con(31)+"Commande inconnue: '{}'".format(command)+cof())
            show_prompt(mud, id)
