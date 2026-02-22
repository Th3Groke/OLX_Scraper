import sqlite3


def DBinsertData(data):
    connection = sqlite3.connect("olx_listings.db")
    cursor = connection.cursor()

    cursor.execute(
        "CREATE TABLE IF NOT EXISTS iphones (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, price TEXT, location TEXT, link TEXT)")

    cursor.execute("SELECT link FROM iphones")
    existing_links = {row[0] for row in cursor.fetchall()}
    for element in data:
        if element.link not in existing_links:
            listing = (element.title, element.price,
                       element.location, element.link)
            cursor.execute(
                "INSERT INTO iphones (title,price,location,link) VALUES (?,?,?,?)", listing)
    connection.commit()
    connection.close()


def DBinsertDummy():
    connection = sqlite3.connect("olx_listings.db")
    cursor = connection.cursor()
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS iphones(id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, price TEXT, location TEXT, link TEXT)")

    cursor.execute(
        '''INSERT INTO iphones(title,price,location,link) VALUES("jd","jd","jd","jd")''')

    connection.commit()
    connection.close()


def DBloadData(min_price=None, max_price=None, sort_by=''):
    connection = sqlite3.connect("olx_listings.db")
    cursor = connection.cursor()
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS iphones (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, price TEXT, location TEXT, link TEXT)")

    query = "SELECT price, title, link, id FROM iphones Where 1=1"
    params = []

    if min_price:
        print("jd")
        query += " AND CAST(REPLACE(REPLACE(price, ' zł',''), ' ', '') AS INTEGER) >= ?"
        params.append(int(min_price))
    if max_price:
        query += " AND CAST(REPLACE(REPLACE(price, ' zł', ''), ' ', '') AS INTEGER) <= ?"
        params.append(int(max_price))

    if sort_by == "Price: Low to High":
        query += " ORDER BY CAST(REPLACE(REPLACE(price, ' zł',''), ' ', '') AS INTEGER) ASC"
    elif sort_by == "Price: High to Low":
        query += " ORDER BY CAST(REPLACE(REPLACE(price, ' zł',''), ' ', '') AS INTEGER) DESC"
    elif sort_by == "Alphabetical (A-Z)":
        query += " ORDER BY title ASC"
    else:
        query += " ORDER BY id DESC"

    cursor.execute(query, params)
    data = cursor.fetchall()
    connection.close()
    return data


def DBremoveData(db_id):
    connection = sqlite3.connect("olx_listings.db")
    cursor = connection.cursor()
    cursor.execute("DELETE FROM iphones WHERE id =?", (db_id,))
    connection.commit()
    connection.close()


def readDataBase():
    data = DBloadData()
    for element in data:
        print(element)


def DBclear():
    connection = sqlite3.connect("olx_listings.db")
    cursor = connection.cursor()
    cursor.execute("DROP TABLE iphones")
    connection.commit()
    connection.close()
