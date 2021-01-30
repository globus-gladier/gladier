

def hello_world(data):
    if data.get('message'):
        return data['message']
    raise ValueError('Hello Errors!')
