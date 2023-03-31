from general_helper import *
from api_helper import OneInchApi, OpenOceanApi
from db_helper import DBHelper


if __name__=='__main__':
    orders = Orders()
    profitable_deals = ProfitableDeals()
    tokens = Tokens()
    one_inch_api = OneInchApi()
    open_ocean_api = OpenOceanApi()
    dbh = DBHelper()
    dbh.create_table()
    dbh.delete_deals()
    print("-"*10, 'Start', "-"*10)
    try:
        while True: 
            orders.delete_expired_orders(profitable_deals, dbh)
            items = one_inch_api.get_active_orders()
            old_active_orders = orders.get_orders_list()
            for item in items:
                order = Order().read_order_from_json(item)
                if orders.get_order(item["orderHash"]):
                    if order.makerAsset =='0x412a68a1de737da33e0a326c023c345b343e8092':
                        continue
                    orders.orders[item["orderHash"]].update(order, tokens)
                    

                order.config_order(tokens)
                orders.add_order(order, tokens)

            for orderHash in old_active_orders:
                if orderHash not in [item["orderHash"] for item in items]:
                    order_status = one_inch_api.get_order_status(orderHash)
                    if order_status:
                        if order_status['status'] in ['expired', 'filled', 'canceled', 'not-enough-balance-or-allowance']:
                            print('Order {} is {}'.format(orderHash[-10:], order_status['status']))
                            orders.delete_order(orderHash, profitable_deals, dbh)
                        else:
                            print(order_status['status'])

            for orderHash in orders.orders:
                profit = orders.orders[orderHash].check_order_profit(tokens, open_ocean_api)
                if profit:
                    profitable_deals.add_deal(profit, dbh)
                    print(profit.to_humanable(orders))
            print("-"*10, "NEXT ITERATION", "-"*10)
    finally:
        dbh.close()
