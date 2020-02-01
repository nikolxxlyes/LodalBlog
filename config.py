import os
basedir = os.path.abspath(os.path.dirname(__file__))
class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or "you_wont_dell_yourself"
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    POST_PER_PAGE = 7
    TOPIC_PER_PAGE = 7
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['nikolayesypchuk@gmail.com']
    OPEN_WEATHER_APPID = '59f15f0d844c57412ffd602800d16379'
    OAUTH_CREDENTIALS = {
        'vk': {
            'id': '7291538',
            'secret': 'cHHo5HBpOWADXxkFzVPf'
        },
        'facebook': {
            'id': '469870800631439',
            'secret': '82bab5683aaab36182e13cb4db224183'
        },
        'ok': {
            'id': '512000333516',
            'secret': '75720F301CF6791790367E69',
            'public': 'CNMHBKJGDIHBABABA'
        }
    }