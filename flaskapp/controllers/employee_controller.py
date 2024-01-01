from flask import Blueprint, render_template, request, redirect, url_for, flash
from factory import db
from datetime import datetime
from flask_login import current_user

employee_blueprint = Blueprint('employee', __name__)

@employee_blueprint.route('/employee', methods=['GET'])
def employee_page():
    orders_collection = db['orders']
    recent_orders = list(orders_collection.find().sort('_id', -1).limit(50))
    return render_template('employee.html', orders=recent_orders, user=current_user)

@employee_blueprint.route('/submit_employee_form', methods=['POST'])
def submit_employee_form():
    # 从表单获取数据
    ref_id = request.form.get('ref_id')
    sell_num = request.form.get('sell_num', type=int)
    item_name = request.form.get('item_name')  # 更改为 'item_name'
    sell_date = request.form.get('sell_date')
    # 以下不会在前端提交
    landed_price = request.form.get('landed_price', type=float)
    sale_price = request.form.get('sale_price', type=float)

    

    # 验证 ref_id 是否存在于数据库中
    item = db['items'].find_one({'ref_id': ref_id})
    if not item:
        flash("Ref ID does not exist in database.")
        return redirect(url_for('employee.employee_page'))

    # 验证 sell_num 是否小于等于当前 stock
    if sell_num > item.get('stock', 0):
        flash("Sell Number exceeds current stock.")
        return redirect(url_for('employee.employee_page'))
    
    # 验证 sell_date 格式
    try:
        datetime.strptime(sell_date, '%Y-%m-%d')
    except ValueError:
        flash("Invalid Sell Date format. Use YYYY-MM-DD.")
        return redirect(url_for('employee.employee_page'))


    # 检查数据的有效性
    if not ref_id or not item_name or sell_num is None or not sell_date:
        # 可以在这里添加更多的错误处理
        return redirect(url_for('employee.employee_page'))

    # 将字符串形式的日期转换为 datetime 对象
    try:
        sell_date = datetime.strptime(sell_date, '%Y-%m-%d')
    except ValueError:
        # 错误的日期格式
        return redirect(url_for('employee.employee_page'))
    
    # 如果未提交 landed_price 或 sale_price，使用数据库中的现有值
    if not landed_price or not sale_price:
        landed_price = landed_price if landed_price else item.get('landed_price')
        sale_price = sale_price if sale_price else item.get('sale_price')
    

    user_name = current_user.username  # 获取当前登录用户的用户名
    # 创建一个新的订单对象
    new_order = {
        'ref_id': ref_id,
        'sell_num': sell_num,
        'item_name': item_name,
        'sell_date': sell_date,
        'landed_price': landed_price,  # 新增 'landed_price'
        'sale_price': sale_price,  # 新增 'sale_price'
        'user_name': user_name,
        'timestamp': datetime.now()
    }

    # 将新订单保存到数据库
    orders_collection = db['orders']
    orders_collection.insert_one(new_order)

    # 保存完成后重定向回员工页面
    return redirect(url_for('employee.employee_page'))

@employee_blueprint.route('/search_inventory', methods=['GET'])
def search_inventory():
    ref_id = request.args.get('ref_id')
    if not ref_id:
        flash("Please enter a Ref ID.")
        return redirect(url_for('employee.employee_page'))

    item = db['items'].find_one({'ref_id': ref_id})
    if not item:
        flash(f"No item found for Ref ID: {ref_id}")
    else:
        flash(f"Inventory for {ref_id}: {item.get('stock', 'N/A')}")

    return redirect(url_for('employee.employee_page'))