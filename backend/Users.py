class User:

    # initializing functions with a bunch of potentially relevant things about users of our app
    def __init__(self, name, username, email, password, age, address):

        # the _ before the variable name makes it a PROTECTED variable
        self._name = name
        self._username = username
        self._email = email
        self._password = password
        self._age = age
        self._address = address
        self._logins = 1
        # self._search_history = {}

    # getters
    def get_name(self):
        return self._name

    def get_username(self):
        return self._username

    def get_email(self):
        return self._email

    def get_password(self):
        return self._password

    def get_age(self):
        return self._age

    def get_address(self):
        return self._address

    def get_logins(self):
        return self._logins

    # def get_search_history(self):
    #     return self._search_history

    def return_info(self):
        return {"Name": self._name,
                "Username": self._username,
                "Email": self._email,
                "Password": self._password,
                "Age": self._age,
                "Address": self._address,
                "Logins": self._logins}
                # "Search History": self._search_history}

    def __str__(self):
        return "Name: " + str(self._username) + \
                "\nUsername: " + str(self._username) + \
                "\nEmail: " + str(self._email) + \
                "\nPassword: " + str(self._password) + \
                "\nAge: " + str(self._age) + \
                "\nAddress: " + str(self._address) + \
                "\nLogins: " + str(self._logins)

# # example user
# x = User("Jatin", "jmather", "jatinm2@illinois.edu", "fakepassword", 18, "Champaign, IL")
#
# # prints out all info about the user
# print(x.return_info())

