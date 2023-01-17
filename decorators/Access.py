from clients.MongoClient import monclient
from classes.UserRole import UserRole
from functools import lru_cache
mc = monclient()

@lru_cache
def whitelist(func):
    def wrapper(message):
        find = mc.find('whitelist', {'nickname': message.from_user.username})
        if len(find) > 0:
            return func(message)
    return wrapper

@lru_cache
def whitelist_query(func):
    def wrapper(call):
        find = mc.find('whitelist', {'nickname': call.message.chat.username})
        if len(find) > 0:
            return func(call)
    return wrapper

@lru_cache
def admin(func):
    def wrapper(message):
        user = mc.find('user', {'nickname': message.from_user.username})
        if len(user) == 0:
            return
        if len(user) == 1:
            role = user[0]['role']
            if role == UserRole.ADMIN.value:
                return func(message)
    return wrapper

@lru_cache
def staff(func):
    def wrapper(message):
        user = mc.find('user', {'nickname': message.from_user.username})
        if len(user) == 0:
            return
        if len(user) == 1:
            role = user[0]['role']
            if role == UserRole.STAFF.value:
                return func(message)
    return wrapper

@lru_cache
def customer(func):
    def wrapper(message):
        user = mc.find('user', {'nickname': message.from_user.username})
        if len(user) == 0:
            return
        if len(user) == 1:
            role = user[0]['role']
            if role == UserRole.CUSTOMER.value:
                return func(message)
    return wrapper