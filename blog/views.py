from turtle import title
from flask import render_template, url_for, flash, redirect, request
from blog import app, db, bc
from blog.forms import LoginForm, RegistrationForm, UpdateProfileForm, BlogForm
from blog.models import User, Post, Comments
from flask_login import login_user, current_user, logout_user, login_required
import requests
from blog.utility_func import save_profile_pic, save_blog_pic


@app.route('/')
def home():
 res = requests.get(f'http://quotes.stormconsultancy.co.uk/random.json').json()
 return render_template('home.html', title='Home', res=res)

@app.route("/register", methods=['GET', 'POST'])
def register():
 if current_user.is_authenticated:
   return redirect(url_for('home'))
 form = RegistrationForm()
 if form.validate_on_submit():
    hashed_password = bc.generate_password_hash(form.password.data).decode('utf-8')
    user = User(username=form.username.data, email=form.email.data, password=hashed_password)
    db.session.add(user)
    db.session.commit()
    flash(f'Account created for {form.username.data}! You can Log in any time', 'secondary')
    return redirect(url_for('login'))
 return render_template('register.html', title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
 if current_user.is_authenticated:
   return redirect(url_for('home'))
 form = LoginForm()
 
 if form.validate_on_submit():
  user = User.query.filter_by(email=form.email.data).first()
  if user and bc.check_password_hash(user.password, form.password.data):
      login_user(user)
      flash(f'{user.username}, You have been logged in!', 'secondary')
      next_page = request.args.get('next')
      return redirect(next_page) if next_page else redirect(url_for('home'))
  else:
      flash('Login Unsuccessful. Please check email and password', 'danger')
 return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    flash('You have successfully logged out', 'secondary')
    return redirect(url_for('home'))
  
  
@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
  profile_image = url_for('static', filename='profile_pics/' + current_user.profile_image)
  # posts = current_user.posts
  posts = Post.query.filter_by(user_id=current_user.id).order_by(Post.date_posted.desc()).all()
  return render_template('account.html', title='Account', profile_image=profile_image, posts=posts)

@app.route("/update_profile", methods=['GET', 'POST'])
@login_required
def update_profile():
  form = UpdateProfileForm()
  if form.validate_on_submit():
    print(form.username.data, form.email.data, form.bio.data)
    if form.profile_pic.data:
      print(form.profile_pic.data)
      p_name = save_profile_pic(form.profile_pic.data)
      current_user.profile_image = p_name
    current_user.username = form.username.data
    current_user.email = form.email.data
    current_user.description = form.bio.data
    db.session.commit()
    flash('Your account has been updated', 'secondary')
    return redirect(url_for('account'))
  elif request.method == 'GET':
    form.username.data = current_user.username
    form.email.data = current_user.email
    form.bio.data = current_user.description
    
  return render_template('update_profile.html', title='Update Profile', form=form)


@app.route("/blogs", methods=['GET', 'POST'])
def blogs():
  posts = Post.query.order_by(Post.date_posted.desc()).all() 
  return render_template('blogs.html', title='Blogs', posts=posts)


@app.route("/create_pitch", methods=['GET', 'POST'])
@login_required
def create_blog():
  form = BlogForm()
  if form.validate_on_submit():
    print(form.title.data, form.content.data)
    post = Post(title=form.title.data, content=form.content.data, author=current_user)
    db.session.add(post)
    db.session.commit()
    flash('You have posted', 'secondary')
    return redirect(url_for('blogs'))
    
  return render_template('create_blog.html', title='Create Blog', form=form)