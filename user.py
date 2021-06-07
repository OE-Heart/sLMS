from flask_login import UserMixin

class User(UserMixin):
    users = []

    def __init__(self,row):
        self.AID = row['AID']
        self.password = row['password']
        self.name = row['name']
        self.contact = row['contact']
        User.users.append(self)

    def get_id(self):
        return (self.AID)

    @classmethod
    def get(cls,AID):
        for u in cls.users:
            if u.AID == AID:
                return u
        return None
