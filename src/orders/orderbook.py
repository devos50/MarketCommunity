from order import Order

class Orderbook:
    ask_orders = []
    bid_orders = []

    def add_order(self, type, json):
        price = json["price"]
        quantity = json["quantity"]
        order = Order(type, price, quantity)
        if type == 'ask':
            self.ask_orders.append(order)
        elif type == 'bid':
            self.bid_orders.append(order)

    def get_orders_string(self):
        str = "price quantity"
        for order in self.ask_orders:
            str += "\n" + order.price + " " + order.quantity + ""
        return str