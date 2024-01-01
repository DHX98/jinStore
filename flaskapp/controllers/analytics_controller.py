from flask import Blueprint, request, jsonify
from factory import db
from datetime import datetime
from flask_login import login_required
from datetime import datetime, timedelta

analytics_blueprint = Blueprint('analytics', __name__)

from collections import defaultdict
from flask import jsonify

@analytics_blueprint.route('/daily_sales', methods=['GET'])
@login_required
def daily_sales():
    orders_collection = db['orders']
    today = datetime.now()
    start_of_today = datetime(today.year, today.month, today.day)  # 当天的开始
    end_of_today = start_of_today + timedelta(days=1)  # 当天的结束

    today_sales = 0

    # 使用日期范围查询
    order_count = orders_collection.count_documents({'sell_date': {'$gte': start_of_today, '$lt': end_of_today}})
    # print(f"Orders found for {today}: {order_count}")  # 打印找到的订单数量

    orders = orders_collection.find({'sell_date': {'$gte': start_of_today, '$lt': end_of_today}})
    for order in orders:
        # print(order)  # 打印每个订单的详细信息
        if 'sale_price' in order and 'sell_num' in order:
            today_sales += order['sale_price'] * order['sell_num']

    return jsonify({today.strftime('%Y-%m-%d'): today_sales})



@analytics_blueprint.route('/average_sell_time', methods=['GET'])
def average_sell_time():
    ref_id = request.args.get('ref_id')
    orders_collection = db['orders']

    if not ref_id:
        return jsonify({'error': 'No ref_id provided'}), 400

    total_time = 0
    count = 0
    last_buy_date = None

    # 按照时间顺序检索所有相关订单
    for order in orders_collection.find({'ref_id': ref_id}).sort('buy_date', 1):
        if 'buy_date' in order and order['buy_date']:
            last_buy_date = datetime.strptime(order['buy_date'], '%Y-%m-%d')

        if 'sell_date' in order and order['sell_date']:
            sell_date = datetime.strptime(order['sell_date'], '%Y-%m-%d')
        elif last_buy_date:
            sell_date = last_buy_date  # 使用上次的买入日期作为默认值
        else:
            continue  # 如果没有有效的 sell_date 或 last_buy_date，则跳过此订单

        total_time += (sell_date - last_buy_date).total_seconds()
        count += 1

    if count == 0:
        return jsonify({'error': 'No valid orders found for provided ref_id'}), 404

    average_time_days = total_time / count / (24 * 3600)
    return jsonify({'average_sell_time_days': average_time_days})


def calculate_average_sell_time(orders_collection, ref_id):
    orders = list(orders_collection.find({'ref_id': ref_id}))
    total_time = 0
    count = 0
    for order in orders:
        if 'buy_date' in order and 'sell_date' in order and order['buy_date'] and order['sell_date']:
            buy_date = order['buy_date']
            sell_date = order['sell_date']
            total_time += (sell_date - buy_date).total_seconds()
            count += 1
    return total_time / count / (24 * 3600) if count > 0 else None

@analytics_blueprint.route('/all_average_sell_times', methods=['GET'])
def all_average_sell_times():
    orders_collection = db['orders']
    items_collection = db['items']

    average_times = {}
    for item in items_collection.find():
        ref_id = item['ref_id']
        average_time = calculate_average_sell_time(orders_collection, ref_id)
        if average_time is not None:
            average_times[ref_id] = average_time

    return jsonify(average_times)