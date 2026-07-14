from flask_login import UserMixin

# creo oggetto user che mi permette di gestire il login
class User(UserMixin):
    def __init__(self, id, username, email, password, role):
        self.id = id
        self.username = username
        self.email = email
        self.password = password
        self.role = role
        
