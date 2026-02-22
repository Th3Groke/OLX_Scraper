import sqlite3
import re


def clear_price(price_str):
    """Extracts numbers from strings like '2 500 zl' and returns an integer."""
    if not price_str:
        return 0
    cleaned = re.sub(r'\D', '', price_str)
    return int(cleaned) if cleaned else 0


def DBinsertData(data):
    connection = sqlite3.connect("olx_listings.db")
    cursor = connection.cursor()

    cursor.execute(
        "CREATE TABLE IF NOT EXISTS listings (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, price TEXT, price_int INTEGER, location TEXT, link TEXT UNIQUE)")

    cursor.execute("SELECT link FROM listings")
    existing_links = {row[0] for row in cursor.fetchall()}
    for element in data:
        if element.link not in existing_links:
            price_num = clear_price(element.price)
            listing = (element.title, element.price, price_num,
                       element.location, element.link)
            cursor.execute(
                "INSERT INTO listings (title,price,price_num,location,link) VALUES (?,?,?,?,?)", listing)
    connection.commit()
    connection.close()


def DBinsertDummy():
    connection = sqlite3.connect("olx_listings.db")
    cursor = connection.cursor()
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS listings(id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, price TEXT, location TEXT, link TEXT)")

    cursor.execute(
        '''INSERT INTO listings(title,price,location,link) VALUES("jd","jd","jd","jd")''')

    connection.commit()
    connection.close()


def DBloadData(min_price=None, max_price=None, sort_by=''):
    connection = sqlite3.connect("olx_listings.db")
    cursor = connection.cursor()
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS listings (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, price TEXT, location TEXT, link TEXT)")

    query = "SELECT price, title, link, id FROM listings Where 1=1"
    params = []

    if min_price:
        query += " AND price_int >= ?"
        params.append(int(min_price))
    if max_price:
        query += " AND price_int <= ?"
        params.append(int(max_price))

    if sort_by == "Price: Low to High":
        query += " ORDER BY price_int ASC"
    elif sort_by == "Price: High to Low":
        query += " ORDER BY price_int DESC"
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
    cursor.execute("DELETE FROM listings WHERE id =?", (db_id,))
    connection.commit()
    connection.close()


def readDataBase():
    data = DBloadData()
    for element in data:
        print(element)


def DBclear():
    connection = sqlite3.connect("olx_listings.db")
    cursor = connection.cursor()
    cursor.execute("DROP TABLE listings")
    connection.commit()
    connection.close()
