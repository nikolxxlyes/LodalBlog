from blog import app, db
from blog.models import User,Post,Topic
"""
Заполняет базу юзерами, темами и постами для теста
"""
#Закоментируйте следующие две строчки для работы с реальной базой
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
db.create_all()

#создание юзеров
users = [User(username="admin_{}".format(i),email=f'admin{i}@gmail.com') for i in range(11,20)]
db.session.add_all(users)
db.session.commit()
#ввод тем
topics = [Topic(name = f"New topic {user.username}", user_id=user.id) for user in users]
db.session.add_all(topics)
db.session.commit()
#ввод постов
posts = [Post(body= f"New post {user.username}",user_id=user.id, topic_id=topic.id) for topic in topics for user in users]
db.session.add_all(posts)

#Установка паролей
for i,user in enumerate(users):
    user.set_password(str(i+11))
    print(user.username, str(i + 11))
db.session.commit()

print(users)
print(topics)
print(posts)
