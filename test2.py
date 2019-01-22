import sqlite3
import json
from phpserialize import unserialize

conn = sqlite3.connect('cendrelune.db')

cursor = conn.cursor()
cursor.execute("""SELECT * FROM users""")
data = cursor.fetchall()

print(cursor.description)

data_json = []
header = [i[0] for i in cursor.description]

for i in data:
    data_json.append(dict(zip(header, i)))

print(json.dumps(data_json, indent=4))

