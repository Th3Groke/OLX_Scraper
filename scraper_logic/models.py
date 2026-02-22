class Listing:
    title = ""
    price = ""
    price_int = None
    location = ""
    date = ""
    link = ""

    def __init__(self, title, price,  location, date, link, price_num):
        self.title = title
        self.price = price
        self.location = location
        self.date = date
        self.link = link
        self.price_int = price_num
