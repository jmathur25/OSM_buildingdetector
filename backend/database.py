# see https://dataset.readthedocs.io/en/latest/ for documentation on dataset
import dataset


# call this to initialize the database and get access to it
def init_backend():
    db = dataset.connect("sqlite:///mydatabase.db")
    table = db["users"]
    return table


"""
Creates a new user with passed info. First checks if one exists with passed information
Info format:
{"name": name,
"username": username,
"email": email,
"password": password,
"age": age,
"address": address,
"logins": 0}
"""
def create_user(info):
    if check_user_exists(info["username"]):
        return False
    table = init_backend()
    info['logins'] = 0
    table.insert(info)
    return True


# call this when a user attempts to sign in. It will update the database IF the users' info checks out
def user_sign_in(info):
    username = info['username']
    password = info['password']
    if check_user_sign_in(username, password) is False:
        return False

    table = init_backend()
    # updates this person's logins
    table.update({"username": username, "logins": table.find_one(username=username)["logins"] + 1}, ["username"])
    return True


# called inside every function. Checks if user is in database given username and password
def check_user_exists(username):
    table = init_backend()
    if table.find_one(username=username) is not None:
        return True
    else:
        return False


def check_user_sign_in(username, password):
    table = init_backend()
    if table.find_one(username=username, password=password) is not None:
        return True
    else:
        return False


# call this to see the whole database
def show_database():
    table = init_backend()
    for row in table:
        print(row)


def clear_database():
    table = init_backend()
    table.drop()
