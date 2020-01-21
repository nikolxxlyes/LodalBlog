from blog import app, db, moment
from blog.models import User,Post,Topic, ExchangeRate

@app.shell_context_processor
def make_shell_context():
    return {'app':app, 'db': db, 'User':User, 'Post':Post,'Topic':Topic,"moment":moment,
            "ExchangeRate":ExchangeRate}