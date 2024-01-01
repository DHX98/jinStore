from flask import Flask
from flask_login import LoginManager
from pymongo import MongoClient

# 全局变量
db = None
users = None

def create_app():
    global db, users

    app = Flask(__name__, template_folder='views')
    app.secret_key = '123456'

    # Flask-Login setup
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    # MongoDB连接设置
    client = MongoClient("mongodb://localhost:27017/")
    db = client["sales_db"]
    users = db["users"]

    # 注册蓝图
    from controllers.auth_controller import auth_blueprint
    from controllers.main_controller import main_blueprint
    from controllers.analytics_controller import analytics_blueprint
    from controllers.employee_controller import employee_blueprint
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(main_blueprint)
    app.register_blueprint(analytics_blueprint)
    app.register_blueprint(employee_blueprint)

    @login_manager.user_loader
    def load_user(user_id):
        from models.user import User
        return User.load_from_db(user_id, users)

    return app
