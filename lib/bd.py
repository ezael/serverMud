def player_exist(conn, nom):
    cursor = conn.cursor()

    cursor.execute("""SELECT * FROM users WHERE name = ?""", (nom,))
    data = cursor.fetchone()

    if data is None:
        return 0
    else:
        return 1


def player_add(conn, params):
    cursor = conn.cursor()

    name = params[0]
    password = params[1]

    sql = """INSERT INTO users (name, pass) VALUES ("%s", "%s")""" % (name, password)
    cursor.execute(sql)
    conn.commit()


def get_zone_description(conn, zone):
    cursor = conn.cursor()

    cursor.execute("""SELECT * FROM zones WHERE nom = ?""", (zone,))
    data = cursor.fetchone()

    return data[2]
