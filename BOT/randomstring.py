import string
import random

def pick(_LENGTH):

    string_pool = string.ascii_uppercase + string.digits

    result = "" 
    for i in range(_LENGTH) :
        result += random.choice(string_pool)

    return result

def picks(_LENGTH):

    string_pool = string.digits

    result = "" 
    for i in range(_LENGTH) :
        result += random.choice(string_pool)

    return result