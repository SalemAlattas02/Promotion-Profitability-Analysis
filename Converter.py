from datetime import date
import requests
import sqlite3

baseURL = 'https://api.frankfurter.dev/v2/rates'

class CurrencyConverter():
    """
    how to use:
    set an object c = CurrencyConverter(base, quote)
    base is the main currency to convert to
    quote is all currencies in the system
    request_rates to request today or a choosen date rates
    request_range_rates to choose rates from a date till today

    then you can use the c.convert(value , quote)
      to convert a value from a currency to base currency    
    """
    TARGET_CURRENCY = "USD"
    Currencies = ['USD', 'EUR', 'INR', 'CAD', 'GBP', 'AUD', 'AED']
    
    def __init__(self, base = TARGET_CURRENCY, quotes = Currencies):
        self.TARGET_CURRENCY = base
        self.Currencies = quotes
        self.db = self.init_database()

    def request_rates(self, date= date.today().strftime("%Y-%m-%d")):
        payload = {"base":self.TARGET_CURRENCY, 
                   # get quote of all currency except the target if its in currencies
                   "quotes": ",".join([x for x in self.Currencies if x != self.TARGET_CURRENCY]), 
                   "date":date}
        return self.request(payload)

    def request_range_rates(self, since):
        payload = {"base":self.TARGET_CURRENCY, 
                   # get quote of all currency except the target if its in currencies
                   "quotes": ",".join([x for x in self.Currencies if x != self.TARGET_CURRENCY]), 
                   "from":since}
        return self.request(payload)
    
    def request(self, payload):
        """
        to do :
        check the database for if the rate exist before request
        """
        response = requests.get(baseURL,params=payload)    
        self.save_rates(response.json())
        return response

    def init_database(self):
        db = sqlite3.connect("rates.db")
        db.execute("""CREATE TABLE IF NOT EXISTS rates (
            date TEXT, base TEXT, quote TEXT, rate REAL,
            PRIMARY KEY (date, base, quote))""")
        return db
        
    def save_rates(self, rates: list):
        self.db.executemany("INSERT OR REPLACE INTO rates VALUES (:date,:base,:quote,:rate)",rates)
        self.db.commit()
    
    def get_rate(self, quote, base = TARGET_CURRENCY, date = date.today().strftime("%Y-%m-%d")):
        "slow and need cach improvement"
        rate = self.db.execute(
            "SELECT rate FROM rates WHERE date=? AND base=? AND quote=?",
            (date, base, quote),
        ).fetchone()
        return rate[0]
    
    def convert(self, value: float, quote, base = TARGET_CURRENCY, date = date.today().strftime("%Y-%m-%d")):
        if (quote == base): 
            return value
        # from base to quote divide
        return value / self.get_rate(quote=quote, base=base, date=date)   
    