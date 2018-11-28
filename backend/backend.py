# see https://dataset.readthedocs.io/en/latest/ for documentation on dataset
import dataset

# based on queries sent from frontend, backend will respond

# call this to initialize backend
# can put this in every function, or frontend can do it and pass to all the below functions
# for now, I have all functions call it
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
    table.insert(info)
    return True


# call this when a user attempts to sign in. It will update the database IF the users' info checks out
def user_sign_in(username=None, password=None):
    if check_user_exists(username, password) is False:
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


# call this whenever a user queries something. The query will be added to the person's search history
# for some reason, dataset doesn't like entries that are lists, so all search history code is commented out for now
# def add_search_history(username=None, password=None, query=None):
#     if check_user_exists(username, password) is False:
#         return False
#     table = init_backend()
#     table.update({"Username": username, "Search History": table.find_one(Username=username)["Search History"].append(query)}, ["Username"])
#     return True


# call this to see the whole database
def show_database():
    table = init_backend()
    for row in table:
        print(row)


def clear_database():
    table = init_backend()
    table.drop()

# create_user({"name": "Jatin",
# "username": "jmather25",
# "email": "jatinm2@illinois.edu",
# "password": "fakepassword123",
# "age": 18,
# "address": "1234 Main Street",
# "logins": 0})

# show_database()
# clear_database()
# show_database()
