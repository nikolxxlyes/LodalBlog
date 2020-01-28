import os
basedir = os.path.abspath(os.path.dirname(__file__))
class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or "you_wont_dell_yourself"
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    POST_PER_PAGE = 7
    TOPIC_PER_PAGE = 7
    OAUTH_CREDENTIALS = {
        'vk': {
            'id': '7291538',
            'secret': 'cHHo5HBpOWADXxkFzVPf'
        },
        'facebook': {
            'id': '469870800631439',
            'secret': '82bab5683aaab36182e13cb4db224183'
        },
        'twitter': {
            'id': '3RzWQclolxWZIMq5LJqzRZPTl',
            'secret': 'm9TEd58DSEtRrZHpz2EjrV9AhsBRxKMo8m3kuIZj3zLwzwIimt'
        },
        'instagram': {
            'id': '3RzWQclolxWZIMq5LJqzRZPTl',
            'secret': 'm9TEd58DSEtRrZHpz2EjrV9AhsBRxKMo8m3kuIZj3zLwzwIimt'
        },
        'ok': {
            'id': '512000333516',
            'secret': '75720F301CF6791790367E69',
            'public': 'CNMHBKJGDIHBABABA'
        }
    }