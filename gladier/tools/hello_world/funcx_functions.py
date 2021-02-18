

def hello_world(message):
    return message


def hello_pause(data):
    import time
    time.sleep(data['delay'])
    return data['message']


def hello_exception(message):
    raise Exception(message)
