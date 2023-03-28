import sqlite3
import time

class DBHelper():
    def __init__(self):
        self.con = sqlite3.connect("./1inch_profitable_trade.db")

    def create_table(self):
        cur = self.con.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS profitable_trades (order_hash text, amount_in real, token_in text, amount_out real, token_out text, amount_out_oo real, profit_amount real, profit_percent real, updated integer)")
        self.con.commit()

    def add_deal(self, deal):
        cur = self.con.cursor()
        cur.execute("INSERT INTO profitable_trades VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (deal.orderHash, deal.amountIn, deal.tokenIn, deal.amountOut, deal.tokenOut, deal.amountOutOO, deal.amountOutOO-deal.amountOut, deal.profitPercent, int(time.time()*1000)))
        self.con.commit()

    def update_deal(self, deal):
        cur = self.con.cursor()
        cur.execute("UPDATE profitable_trades SET amount_in=?, token_in=?, amount_out=?, token_out=?, amount_out_oo=?, profit_amount=?, profit_percent=?, updated=? WHERE order_hash=?", (deal.amountIn, deal.tokenIn, deal.amountOut, deal.tokenOut, deal.amountOutOO, deal.amountOutOO-deal.amountOut, deal.profitPercent, int(time.time()*1000), deal.orderHash))
        self.con.commit()        
    
    def delete_deal(self, order_hash):
        cur = self.con.cursor()
        cur.execute("DELETE FROM profitable_trades WHERE order_hash=?", (order_hash,))
        self.con.commit()
    
    def delete_deals(self):
        cur = self.con.cursor()
        cur.execute("DELETE FROM profitable_trades")
        self.con.commit()
    
    def get_deals(self):
        cur = self.con.cursor()
        cur.execute("SELECT * FROM profitable_trades")
        return cur.fetchall()
    
    def close(self):
        self.con.close()