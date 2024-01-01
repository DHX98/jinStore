from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, username, password, user_type):
        self.id = username
        self.username = username
        self.password = password
        self.user_type = user_type

    @staticmethod
    def load_from_db(user_id, users_db):

        user_data = users_db.find_one({"username": user_id})
        
        if user_data:
            u = User(username=user_data['username'], password=user_data['password'], user_type=user_data['user_type'])
            print('loaded user ',u)
            return u
        return None
    
    
