def init_classes(conn):
    cursor = conn.cursor()

    cursor.execute("""SELECT * FROM classes""")
    rows = cursor.fetchall()

    classes = {}

    for row in rows:
        classes[ row[1] ] = [
            row[2],
            row[3],
            row[4],
            row[5],
            row[6],
            row[7],
        ]

    return classes
