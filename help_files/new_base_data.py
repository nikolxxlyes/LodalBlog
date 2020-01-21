from blog import app, db
from blog.models import User,Post,Topic,ExchangeRate
from exchange_rates import get_currency_pair,set_currency_pair
"""
Заполняет базу юзерами, темами и постами для теста
"""
#Настройка для тестов
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
db.create_all()

#создание юзеров
users = [User(username="admin_{}".format(i),email=f'admin{i}@gmail.com') for i in range(11,20)]
for user in users:
    db.session.add(user)
db.session.commit()
#ввод тем
topics = [Topic(name = f"new topic _{user.username}", user_id=user.id) for user in users]
for topic in topics:
    db.session.add(topic)
db.session.commit()
#ввод постов
posts = [Post(body= f"new post {user.username}",user_id=user.id, topic_id=topic.id) for topic in topics for user in users]
for post in posts:
    db.session.add(post)

#Установка паролей
for i,user in enumerate(users):
    user.set_password(str(i+11))
    print(user.username, str(i + 11))
db.session.commit()

print(users)
print(topics)
print(posts)
