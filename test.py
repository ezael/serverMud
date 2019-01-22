import sqlite3
import socket


from lib.init import *

conn = sqlite3.connect('cendrelune.db')

classes = init_classes(conn)

frc, dex, con, int, sag, cha = classes['guerrier']

hote = ''
port = 4444

monServeur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
monServeur.bind( (hote, port) )
monServeur.listen(5)

print("""ecoute en cours...""")

monClient, infosConnexion = monServeur.accept()
dfgdf
while 1:
    msgRecu = monClient.recv(1024)

    if (msgRecu == 'fin'):
        monClient.close()
        monServeur.close()
    else:
        print(msgRecu.decode('utf-8', 'ignore'))
