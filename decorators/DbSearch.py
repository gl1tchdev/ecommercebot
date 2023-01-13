def fullpath(func):
    def wrapper(obj, path):
        result = func(obj, path)
        if type(result) is dict:
            return {(path + '/'+ str(key)): result[key] for key in result}
        else:
            return result
    return wrapper
