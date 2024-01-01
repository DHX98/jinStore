from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from factory import db
from datetime import datetime

main_blueprint = Blueprint('main', __name__)

@main_blueprint.route('/', methods=['GET', 'POST'])
@login_required
def index():
    sales_collection = db['items']
    orders_collection = db['orders']  # 新增一个用于存储订单的集合

    if request.method == 'POST':
       
        ref_id = request.form.get('ref_id')
        sell_num = request.form.get('sell_num', type=int) if request.form.get('sell_num', type=int) else 0
        buy_num = request.form.get('buy_num', type=int) if request.form.get('buy_num', type=int) else 0
        item_name = request.form.get('item_name')  # 更改为 'item_name'
        buy_date = request.form.get('buy_date')
        sell_date = request.form.get('sell_date')
        user_name = current_user.username  # 获取当前登录用户的用户名
        landed_price = request.form.get('landed_price', type=float)
        sale_price = request.form.get('sale_price', type=float)
        # 添加验证逻辑
        if sell_num == 0 and buy_num == 0:
            flash("Please enter at least one of Sell Number or Buy Number.")
            return redirect(url_for('main.index'))
        if not buy_date and not sell_date:
            flash("Please enter at least one of Sell Date or Buy Date.")
            return redirect(url_for('main.index'))
        if not ref_id or not item_name:
            flash("Ref_id or item_name not uploaded")
            return redirect(url_for('main.index'))
        # 验证 item_name 是否与 ref_id 匹配
        item = sales_collection.find_one({'ref_id': ref_id})
        if item and item['item_name'] != item_name:
            flash("Item name does not match with ref_id.")
            return redirect(url_for('main.index'))
        # 提交了sell_num,那么必须填写sell_date,如果用户提交了buy_num, 必须填写buy_date
        if sell_num > 0 and not sell_date:
            flash("Sell Date must be provided when Sell Number is entered.")
            return redirect(url_for('main.index'))
        if buy_num > 0 and not buy_date:
            flash("Buy Date must be provided when Buy Number is entered.")
            return redirect(url_for('main.index'))
        
        # 检查当 sell_num 被输入时，item 是否存在于数据库中
        if sell_num > 0:
            item = sales_collection.find_one({'ref_id': ref_id})
            if not item:
                flash("Item does not exist for the provided Ref ID.")
                return redirect(url_for('main.index'))
        # Check if landed price or sale price is not submitted
        if not landed_price or not sale_price:
            # Retrieve the item from the database
            item = sales_collection.find_one({'ref_id': ref_id})

            # Use existing values if available, otherwise flash error
            if item:
                landed_price = landed_price if landed_price else item.get('landed_price')
                sale_price = sale_price if sale_price else item.get('sale_price')
            else:
                flash("Landed price and sale price must be provided for new items.")
                return redirect(url_for('main.index'))
        
        buy_date = datetime.strptime(buy_date, '%Y-%m-%d') if buy_date else None
        sell_date = datetime.strptime(sell_date, '%Y-%m-%d') if sell_date else None
        # 更新库存
        new_stock = 0

        # 检查库存
        item = sales_collection.find_one({'ref_id': ref_id})
        if item:
            current_stock = item.get('stock', 0)
            if sell_num > current_stock:
                flash("Sell Number exceeds current stock.")
                return redirect(url_for('main.index'))
            new_stock = current_stock - sell_num + buy_num
        else:
            if buy_num < 1:
                flash("Invalid Buy Number.")
                return redirect(url_for('main.index'))
            new_stock = buy_num
        
        # 更新销售数据到销售表（商品表）
        update_data = {
            '$inc': {'sell_num': sell_num, 'buy_num': buy_num},
            '$set': {'item_name': item_name, 'user_name': user_name, 'stock': new_stock, 'landed_price': landed_price,
        'sale_price': sale_price}
        }
        sales_collection.update_one({'ref_id': ref_id}, update_data, upsert=True)

        # 保存订单信息到order表
        order_data = {
            'ref_id': ref_id,
            'sell_num': sell_num,
            'buy_num': buy_num,
            'item_name': item_name,
            'buy_date': buy_date,
            'sell_date': sell_date,
            'user_name': user_name,
            'landed_price': landed_price,
            'sale_price': sale_price,
            'timestamp': datetime.now()
        }
        orders_collection.insert_one(order_data)

        return redirect(url_for('main.index'))

    sales_data = list(sales_collection.find({}))
    return render_template('index.html', sales_data=sales_data)
