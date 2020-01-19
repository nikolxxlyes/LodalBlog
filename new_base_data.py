from blog import app, db
from blog.models import User,Post,Topic
"""
Заполняет базу юзерами, темами и постами для теста
"""

users,topics, posts   = [], [],[]
for i in range(11,20):
    users.append({"username" : "admin_{}".format(i),'email': f'admin{i}@gmail.com'})
# users = [{"username" : "admin{}".format(i),'email': f'admin{i}@gmail.com'} for i in range(11,20)]
users = [User(**user) for user in users]

for user in users:
    db.session.add(user)
    db.session.commit()
    topics.append({"name" : f"new topic _{user.username}", "user_id" : str(user.id)})
topics = [Topic(**topic) for topic in topics]

for topic in topics:
    db.session.add(topic)
    db.session.commit()
    for user in users:
        posts.append({"body" : f"new post {user.username}", "user_id" : str(user.id), "topic_id" : str(topic.id)})

posts = [Post(**post) for post in posts]

for post in posts:
    db.session.add(post)

for i,user in enumerate(users):
    print(user.username, str(i+11))
    user.set_password(str(i+11))

# print(users)
# print(topics)
# print(posts)
db.session.commit()