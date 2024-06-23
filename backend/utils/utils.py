import bcrypt


JWT_KEY = "JWT_Private_Key"

def hash_password(password):
    salt = bcrypt.gensalt()
    hash_password = bcrypt.hashpw(password.encode("utf-8"), salt)
    return salt, hash_password

def check_password(password, hashedPassword):
    if bcrypt.checkpw(password.encode('utf-8'), hashedPassword):
        return True
    return False
