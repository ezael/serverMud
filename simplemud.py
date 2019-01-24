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

texte = []

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
        txt(mud, id, "")
        txt(mud, id, ctxt(37, "--- bienvenue ---"))
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
                txt(mud, id, "")
                txt(mud, id, "{} a quitte le jeu.".format(players[id]["name"]))
                show_prompt(mud, id)

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
                txt(mud, id, "")
                txt(mud, id, "Ce nom de joueur existe deja dans notre base !")
                txt(mud, id, "Merci d'en choisir un autre ou de vous connecter en tapant la commande :")
                txt(mud, id, "\033[1mconnect \033[0m "+theParams[0]+" <motdepasse>\n")

                show_prompt(mud, id)
            else:
                # on crée le nouveau joueur
                player_add(conn, theParams)
                players[id]["connexion"] = 1

                # on l'enregistre dans la table temporaraire des joueurs en ligne
                players[id]["name"] = theParams[0]
                players[id]["password"] = theParams[1]

                # on lui affiche un message de bienvenue
                txt(mud, id, "")
                txt(mud, id, "Nouveau commpte créé !")
                txt(mud, id, "Bienvenue, {}.\n".format(players[id]["name"]))

                show_prompt(mud, id)

                # on le place dans la zone de début du jeu
                # on lui affiche la description de la zone
                players[id]["room"] = "Tavern"
                #mud.send_message(id, get_zone_description(conn, "Tavern"))

                # on prévient les autres joueurs connectés qu'il vient d'arriver
                #for pid, pl in players.items():
                #    if pid != id:
                #        # send each player a message to tell them about the new player
                #        mud.send_message(id, "")
                #        mud.send_message(pid, "\033[23;2H\033[31;1m{} vient de se connecter.\033[0m".format( players[id]["name"]))

                #        show_prompt(mud, id)

        # 'aide' command
        elif command == "m" or command == "M":

            if not params:
                txt(mud, id, "")
                txt(mud, id, "Menu:")
                txt(mud, id, "-------------------------------------------")
                txt(mud, id, "[s] Changer de station")
                txt(mud, id, "[v] Etat de la station")
                txt(mud, id, "[c] Constructions")
                txt(mud, id, "[r] Recherches")
                txt(mud, id, "[f] Flottes")
                txt(mud, id, "[n] Navires")

                show_prompt(mud, id)

        # 'say' command
        elif command == "dire" and players[id]["connexion"] == 1:

            # go through every player in the game
            for pid, pl in players.items():
                # if they're in the same room as the player
                if players[pid]["room"] == players[id]["room"]:
                    # send them a message telling them what the player said
                    txt(mud, id, "")
                    txt(mud, pid, "{} dit: {}".format(players[id]["name"], params))
                    show_prompt(mud, id)

        # 'look' command
        elif command == "regarder" or command == 'reg':

            if players[id]["connexion"] == 1:
                # store the player's current room
                rm = rooms[players[id]["room"]]

                # send the player back the description of their current room
                txt(mud, id, "")
                txt(mud, id, get_zone_description(conn, players[id]["room"]))
                show_prompt(mud, id)

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
                txt(mud, id, "Joueurs presents: {}".format(", ".join(playershere)))

                # send player a message containing the list of exits from this room
                txt(mud, id, "Sorties visibles: {}".format(", ".join(rm["exits"])))

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
                        txt(mud, pid, "{} left via exit '{}'".format(players[id]["name"], ex))

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
                        txt(mud, pid, "{} arrived via exit '{}'".format(players[id]["name"], ex))

                # send the player a message telling them where they are now
                txt(mud, id, "Vous arrivez a: '{}'".format(players[id]["room"]))

            # the specified exit wasn't found in the current room
            else:
                # send back an 'unknown exit' message
                txt(mud, id, "Sortie inconnue: '{}'".format(ex))

        # some other, unrecognised command
        else:
            # send back an 'unknown command' message
            txt(mud, id, "Commande inconnue: '{}'".format(command))
            show_prompt(mud, id)
