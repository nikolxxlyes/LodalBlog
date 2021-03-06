# -*- coding: utf-8 -*-
from blog import app,db
from flask import render_template, url_for, redirect,flash,session
from .forms import LoginForm,RegistrationForm,EditProfileForm,EmailForm, \
	NewTopicForm, EditTopicForm, NewPostForm, EditPostForm, ResetEmailForm,\
	ResetPasswordForm
from flask_login import logout_user,login_user,current_user,login_required
from blog.models import User, Topic, Post,ExchangeRate, WeatherPoint as W_p
from flask import request
from werkzeug.urls import url_parse
from datetime import datetime
from blog.lib.exchange_rates import set_currency_pair
from blog.lib.weather import get_city,geo_import
#oauth
from blog.oauth import OAuthSignIn
#reset_password
from blog.email import send_password_reset_email

@app.route('/')
@app.route('/index')
def index():
	return render_template('index.html', title='Home',)

@app.route('/login', methods=['POST', 'GET'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(username=form.username.data).first()
		if user is None or not user.check_password(form.password.data):
			flash('Invalid username or password')
			return redirect(url_for('login'))
		login_user(user, remember=form.remember_me.data)
		current_user.forget_password = False
		next_page = request.args.get('next')
		if not next_page or url_parse(next_page).netloc != '':
			next_page = url_for('index')
		return redirect(next_page)
	return render_template('login.html', title='Sign In', form=form, forget_password=True)


@app.route('/register', methods=['POST', 'GET'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	form = RegistrationForm()
	if form.validate_on_submit():
		user = User(username=form.username.data, email=form.email.data)
		user.set_password(form.password.data)
		db.session.add(user)
		db.session.commit()
		flash('Congratulations, you are now a registered user!')
		return redirect(url_for('login'))
	return render_template('register.html', title='Register', form=form)

@app.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('index'))

@app.route('/u/<username>')
@login_required
def user(username):
	user = User.query.filter_by(username=username).first_or_404()
	page = request.args.get('page', 1, type=int)
	filter = Post.user_id==user.id if current_user == user else Post.user_id==user.id,Post.active == 1
	posts = Post.query.filter(*filter).order_by(Post.timestamp.desc()).paginate(
		page, app.config['POST_PER_PAGE'], False)
	next_url = url_for('user',username=user.username, page=posts.next_num) if posts.has_next else None
	prev_url = url_for('user',username=user.username, page=posts.prev_num) if posts.has_prev else None
	return render_template('user.html', title="Profile", user=user, posts=posts.items,next_url=next_url,
						   prev_url=prev_url)

@app.before_request
def before_request():
	if current_user.is_authenticated:
		current_user.last_seen = datetime.utcnow()
		db.session.commit()

@app.route('/u/<username>/edit_profile', methods=['POST', "GET"])
@login_required
def edit_profile(username):
	form = EditProfileForm()
	if form.validate_on_submit():
		current_user.username = form.username.data
		current_user.email = form.email.data
		current_user.about_me = form.about_me.data
		if form.new_password.data:
			current_user.set_password(form.new_password.data)
		db.session.commit()
		flash('Your changes have been saved.')
		return redirect(url_for('user',username=form.username.data))
	elif request.method == "GET":
		form.username.data = current_user.username
		form.email.data = current_user.email
		form.about_me.data = current_user.about_me
	return render_template('edit_profile.html', title='Edit Profile', form=form)

@app.route('/topics')
def topics():
	page = request.args.get('page',1,type=int)
	topics = Topic.query.order_by(Topic.timestamp.desc()).paginate(
		page,app.config['TOPIC_PER_PAGE'],False)
	next_url = url_for('topics', page=topics.next_num) if topics.has_next else None
	prev_url = url_for('topics', page=topics.prev_num) if topics.has_prev else None
	icon_url = '//icon-icons.com/icons2/2110/PNG/{}/comment_icon_131036.png'.format(48)
	for topic in topics.items:
		topic.count_posts = topic.posts.filter(Post.active==1).count()
		topic.last_post = topic.posts.filter(Post.active==1).order_by(Post.timestamp.desc()).first()
		topic.last_time = topic.last_post.timestamp if topic.last_post else topic.timestamp
	return render_template('topics.html',title='Topics', topics=topics.items,next_url=next_url,
						   prev_url=prev_url,icon_url=icon_url)

@app.route('/topic/<t>', methods=['GET', 'POST'])
def topic(t):
	topic = Topic.query.get(t)
	page = request.args.get('page', 1, type=int)
	posts = topic.posts.filter_by(active=1).order_by(Post.timestamp.desc()).paginate(
			page,app.config['POST_PER_PAGE'],False)
	next_url = url_for('topic',t=t, page=posts.next_num) if posts.has_next else None
	prev_url = url_for('topic',t=t, page=posts.prev_num) if posts.has_prev else None
	#add post in topic
	form = NewPostForm()
	if form.validate_on_submit():
		session['data_post'] = {'body': form.body.data}
		# flash(form.body.data)
		return redirect(url_for('new_post', t=t,))
	return render_template('topic.html',title='Topic', topic=topic, posts=posts.items,next_url=next_url,
						   prev_url=prev_url,form=form)

@app.route('/topic/add', methods=['POST', "GET"])
@login_required
def new_topic():
	form = NewTopicForm()
	if form.validate_on_submit():
		user_id = current_user.id
		topic = Topic(name=form.name.data, user_id=user_id)
		db.session.add(topic)
		db.session.commit()
		post = Post(body=form.msg.data, user_id=user_id, topic_id=topic.id)
		db.session.add(post)
		db.session.commit()
		flash('Congratulations, your topic had been added!')
		return redirect(url_for('topics'))
	return render_template('new_topic.html', title='Add topic', form=form)

@app.route('/topic/<t>/edit', methods=["POST", "GET"])
@login_required
def edit_topic(t):
	topic = Topic.query.get(t)
	if topic.user_id != current_user.id:
		return redirect(url_for('index'))
	form = EditTopicForm(topic.name)
	if form.validate_on_submit():
		topic.name = form.name.data
		db.session.commit()
		flash('Your changes have been saved.')
		return redirect(url_for('topic', t=t))
	elif request.method == "GET":
		form.name.data = topic.name
	return render_template('edit_topic.html',title='Edit Topic', topic=topic, form=form)

@app.route('/add_post', methods=['POST', "GET"])
@login_required
def new_post():
	form = NewPostForm()
	t = request.args.get('t')
	p = request.args.get('p')
	topic = Topic.query.get(t)
	repost = Post.query.get(p).body if p else None
	on_session_data = session.pop('data_post',None)
	if form.validate_on_submit() or on_session_data:
		if on_session_data:
			form.body.data = on_session_data['body']
		user_id = current_user.id
		post = Post(body=form.body.data, user_id=user_id, topic_id=t,parent=p)
		db.session.add(post)
		db.session.commit()
		flash('Congratulations, your post had been added!')
		return redirect(url_for('topic', t=post.topic_id))
	return render_template('new_post.html', title='Add Post', form=form, topic=topic,repost=repost)

@app.route('/<p>/edit', methods=["POST", "GET"])
@login_required
def edit_post(p):
	post = Post.query.get(p)
	if post.user_id != current_user.id:
		return redirect(url_for('index'))
	form = EditPostForm()
	if form.validate_on_submit():
		post.body = form.body.data
		post.active = form.active.data
		db.session.commit()
		flash('Your changes have been saved.')
		return redirect(url_for('user',username=current_user.username))
	elif request.method == "GET":
		form.body.data = post.body
		form.active.data = post.active
	return render_template('edit_post.html',title='Edit Post', topic=topic, form=form,post=post)

@app.route('/follow/<username>')
@login_required
def follow(username):
	user = User.query.filter_by(username=username).first()
	if user is None:
		flash('User {} not found.'.format(username))
		return redirect(url_for('index'))
	if user == current_user:
		flash('You cannot follow yourself!')
		return redirect(url_for('user', username=username))
	current_user.follow(user)
	db.session.commit()
	flash('You are following {}!'.format(username))
	return redirect(url_for('user', username=username))

@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
	user = User.query.filter_by(username=username).first()
	if user is None:
		flash('User {} not found.'.format(username))
		return redirect(url_for('index'))
	if user == current_user:
		flash('You cannot unfollow yourself!')
		return redirect(url_for('user', username=username))
	current_user.unfollow(user)
	db.session.commit()
	flash('You are not following {}.'.format(username))
	return redirect(url_for('user', username=username))

@app.route('/friends_posts')
@login_required
def friends_posts():
	page = request.args.get('page', 1, type=int)
	posts = current_user.followed_posts().paginate(page, app.config['POST_PER_PAGE'], False)
	next_url = url_for('friends_posts', page=posts.next_num) if posts.has_next else None
	prev_url = url_for('friends_posts', page=posts.prev_num) if posts.has_prev else None
	return render_template('friends_posts.html', title="Friends Posts", posts=posts.items, next_url=next_url,
						   prev_url=prev_url)

@app.route('/rates')
def rates():
	pairs = ExchangeRate.query.all()
	if not pairs:
		set_currency_pair(db, ExchangeRate)
		pairs = ExchangeRate.query.all()
	if request.args.get('pull'):
		delta = datetime.utcnow() - pairs[0].timestamp
		delta = delta.seconds // 3600
		if delta >= 1:
			old_pairs = pairs
			set_currency_pair(db,ExchangeRate)
			pairs = ExchangeRate.query.all()
			for old in old_pairs:
				for pair in pairs:
					if old.currency_pair == pair.currency_pair:
						delta_buy = round(pair.buy - old.buy,2)
						delta_sale = round(pair.sale - old.sale,2)
						pair.delta_buy = f"(+{delta_buy})" if delta_buy >= 0 else f"({delta_buy})"
						pair.delta_sale = f"(+{delta_sale})" if delta_sale >= 0 else f"({delta_sale})"
		else:
			flash("Новых валютных котировок еще не прислали.")
	return render_template('rates.html', title="Exchange rates", pairs=pairs)


@app.route('/share')
def share():
	pass

@app.route('/weather', methods=["POST", "GET"])
def weather():
	icon_url = "http://openweathermap.org/img/wn/{}@2x.png"
	try:
		loc = request.args.get('loc')
		city,c_code = get_city(loc)
		# print(city, ' - current city')
	except TypeError:
		city = 'kyiv'
		c_code = 'ua'
		# print('No response')
	except ValueError:
		print('no valid coordinates')
		flash("Your coordinates is not valid.")
	except Exception as e:
		print(e,type(e))
	weathers = W_p.query.filter_by(city=city).all()
	try:
		if datetime.utcnow() >= weathers[0].timestamp:
			for weather in weathers:
				db.session.delete(weather)
			db.session.commit()
			geo_import(city, c_code)
			weathers = W_p.query.filter_by(city=city).all()
	except IndexError:
		geo_import(city, c_code)
		weathers = W_p.query.filter_by(city=city).all()
	except TypeError:
		pass
	# if request.method == "POST":
	# 	return redirect(url_for('index'))
	return render_template('weather.html', title="Weather", weathers=weathers, icon_url=icon_url )

@app.route('/authorize/<provider>')
def oauth_authorize(provider):
	if not current_user.is_anonymous:
		return redirect(url_for('index'))
	oauth = OAuthSignIn.get_provider(provider)
	return oauth.authorize()

@app.route('/callback/<provider>')
def oauth_callback(provider):
	if not current_user.is_anonymous:
		return redirect(url_for('index'))
	oauth = OAuthSignIn.get_provider(provider)
	social_id, username, email = oauth.callback()
	if social_id is None:
		flash('Authentication failed.')
		return redirect(url_for('index'))
	user = User.query.filter_by(social_id=social_id).first()
	if not user:
		if User.query.filter_by(username=username).first():
			new_username = username + " Original"
			flash(f"Похоже пользователь с именем '{username}' уже существует. Мы зарегистрировали вас как '{new_username}'.")
			flash("У вас будет возможность изменить username в личном кабинете.")
			username = new_username
		else:
			flash('Congratulations, you are now a registered user!')
		user = User(username=username, email=email,social_id=social_id)
		db.session.add(user)
		db.session.commit()
	login_user(user, True)
	if not email:
		return redirect(url_for('finish_register'))
	return redirect(url_for('index'))

@app.route('/finish_register',methods=["GET",'POST'])
@login_required
def finish_register():
	if current_user.email:
		return redirect('index')
	form = EmailForm()
	if form.validate_on_submit():
		current_user.email = form.email.data
		db.session.commit()
		flash('Регистрация завершена успешно! Установите пароль от учётной записи в личном кабинете.')
		return redirect(url_for('index'))	
	return render_template('finish_register.html',form=form)

@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	form = ResetEmailForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user:
			send_password_reset_email(user)
		flash('Check your email for the instructions to reset your password')
		return redirect(url_for('login'))
	return render_template('reset_password_request.html',title='Reset Password', form=form)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	user = User.verify_reset_password_token(token)
	if not user:
		return redirect(url_for('index'))
	form = ResetPasswordForm()
	if form.validate_on_submit():
		user.set_password(form.password.data)
		db.session.commit()
		flash('Your password has been reset.')
		return redirect(url_for('login'))
	return render_template('reset_password.html', form=form)

