from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from models.user import User
from factory import db, users

auth_blueprint = Blueprint('auth', __name__)

@auth_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user_data = users.find_one({"username": username})
        if user_data and user_data['password'] == password:
            user = User(username=username, password=password, user_type=user_data['user_type'])
            login_user(user)
            
            # 检查用户类型并重定向到相应页面
            if user.user_type == 'admin':
                return redirect(url_for('main.index'))
            elif user.user_type == 'employee':
                return redirect(url_for('employee.employee_page'))  # 确保此路由已定义

        else:
            flash('Invalid username or password')
    return render_template('login.html')


@auth_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user_type = request.form.get('user_type')
        admin_password = request.form.get('admin_password')

        # 用您的管理员密码替换此处
        admin_password_expected = "555"

        if users.find_one({"username": username}):
            print('Username already exists')
            flash('Username already exists', 'error')
        elif user_type in ['admin', 'employee'] and admin_password != admin_password_expected:
            print('Invalid admin password')
            flash('Invalid admin password', 'error')
        else:
            users.insert_one({"username": username, "password": password, "user_type": user_type})
            return redirect(url_for('auth.login'))

    return render_template('register.html')




@auth_blueprint.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))