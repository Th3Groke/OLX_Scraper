class Listing:
    title = ""
    price = ""
    price_int = None
    location = ""
    date = ""
    link = ""

    def __init__(self, title, price, price_int, location, date, link):
        self.title = title
        self.price = price
        self.price_int = price_int
        self.location = location
        self.date = date
        self.link = link
