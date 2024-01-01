from datetime import datetime

class Order:
    def __init__(self, ref_id, sell_num, buy_num, name, buy_date, sell_date):
        self.ref_id = ref_id
        self.sell_num = sell_num
        self.buy_num = buy_num
        self.name = name
        self.buy_date = buy_date
        self.sell_date = sell_date

    @staticmethod
    def from_form(request_form):
        ref_id = request_form.get('ref_id')
        sell_num = request_form.get('sell_num')
        buy_num = request_form.get('buy_num')
        name = request_form.get('name')
        buy_date = request_form.get('buy_date')
        sell_date = request_form.get('sell_date')

        # Optional: Convert dates from string to datetime objects
        buy_date = datetime.strptime(buy_date, '%Y-%m-%d') if buy_date else None
        sell_date = datetime.strptime(sell_date, '%Y-%m-%d') if sell_date else None

        return Order(ref_id, sell_num, buy_num, name, buy_date, sell_date)

    # Additional methods to interact with database or perform other operations can be added here.
