# routes.py
from flask import render_template, flash, request, redirect, url_for
from flask_login import login_user, current_user, logout_user, login_required
from forms import NamerForm, UserForm, PostForm, LoginForm, SearchForm
from models import Users, Posts
from app import app, db
from werkzeug.security import generate_password_hash

# Create a route decorator
@app.route('/')
def index():
	return render_template('index.html')

# Create custom error page
# Invalid error
@app.errorhandler(404)
def page_not_found(e):
	return render_template('404.html'), 404

# Internal server error
@app.errorhandler(500)
def page_not_found(e):
	return render_template('500.html'), 500

# Create Name 
@app.route('/name', methods = ['GET', 'POST'])
def name():
	name = None
	form = NamerForm()
	# validate form
	if form.validate_on_submit():
		name = form.name.data
		form.name.data = ''
		flash('Form Submitted Successfully')
	return render_template('name.html', name = name, form = form)

# Create Add User
@app.route('/user/add', methods=['GET', 'POST'])
def add_user():
    name = None
    form = UserForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            # Hash Password
            # hashed_pw = generate_password_hash(form.password_hash.data, "sha256")
            hashed_pw = generate_password_hash(form.password_hash.data, method='pbkdf2:sha256', salt_length=8)
            new_user = Users(name=form.name.data, email=form.email.data, username=form.username.data, password_hash=hashed_pw)
            db.session.add(new_user)
            db.session.commit()
            name = form.name.data
            form.name.data = ''
            form.email.data = ''
            form.username.data = ''
            form.password_hash.data = ''
            flash('User Added Successfully')
    our_users = Users.query.order_by(Users.date_added).all()
    return render_template('add_user.html', form=form, name=name, our_users=our_users)

@app.route('/user/<name>')
def user(name):
	return render_template('user.html', name=name)

# Create Update Users Details
@app.route('/update/<int:id>', methods = ['GET', 'POST'])
def update(id):
	form = UserForm()
	name_to_update = Users.query.get_or_404(id)
	if request.method == 'POST':
		name_to_update.name = request.form.get('name', name_to_update.name)
		name_to_update.email = request.form.get('email', name_to_update.email)
		name_to_update.username = request.form.get('username', name_to_update.username)
		password = request.form.get('password_hash')
		if password:
			name_to_update.password_hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)

		try:
			db.session.commit()
			flash('User Updated Successfully!')
			return render_template('update.html', form=form, name_to_update=name_to_update)
		except:
			flash('Errrr.. Looks like there was a problem!')
			return render_template('update.html', form=form, name_to_update=name_to_update)
	else:
		return render_template('update.html', form=form, name_to_update=name_to_update)

# Create Delete User
@app.route('/delete/<int:id>')
def delete(id):
    user_to_delete = Users.query.get_or_404(id)
    name = None
    form = UserForm()
    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash('User Deleted Successfully')
        our_users = Users.query.order_by(Users.date_added).all()
        return render_template('add_user.html', form=form, name=name, our_users=our_users)
    except:
        flash('Whoops! There was a problem deleting this user')
        our_users = Users.query.order_by(Users.date_added).all()
        return render_template('add_user.html', form=form, name=name, our_users=our_users)

# Create Add Post
@app.route('/add-post', methods = ['GET', 'POST'])
@login_required
def add_post():
	form = PostForm()
	if form.validate_on_submit():
		poster = current_user.id
		post = Posts(title = form.title.data, content = form.content.data, poster_id = poster, slug = form.slug.data)
		form.title.data = ''
		form.content.data = ''
		# form.author.data = ''
		form.slug.data = ''
		# Add data to the database
		db.session.add(post)
		db.session.commit()
		flash('Blog Post Submitted Successfully')
	return render_template('add_post.html', form = form)

# Create Show All Posts
@app.route('/posts')
def posts():
	# Getting all the post from database
	posts = Posts.query.order_by(Posts.date_posted)
	return render_template('posts.html', posts=posts)

# Create Show single post
@app.route('/posts/<int:id>')
def post(id):
	post = Posts.query.get_or_404(id)
	return render_template('post.html', post = post)

# Create Edit Post
@login_required
@app.route('/posts/edit/<int:id>', methods=['GET', 'POST'])
def edit_post(id):
	post = Posts.query.get_or_404(id)
	form = PostForm()
	if form.validate_on_submit():
		post.title = form.title.data
		post.slug = form.slug.data
		post.content = form.content.data
		# Update Database
		db.session.add(post)
		db.session.commit()
		flash("Post Has Been Updated!")
		return redirect(url_for('post', id=post.id))
	
	if current_user.id == post.poster_id or current_user.id == 14:
		form.title.data = post.title
		form.slug.data = post.slug
		form.content.data = post.content
		return render_template('edit_post.html', form=form)
	else:
		flash("You Aren't Authorized To Edit This Post...")
		posts = Posts.query.order_by(Posts.date_posted)
		return render_template("posts.html", posts=posts)

# Create Delete Post
@app.route('/post/delete/<int:id>')
@login_required
def delete_post(id):
    post_to_delete = Posts.query.get_or_404(id)
    id = current_user.id
    if id == post_to_delete.poster.id:
        try:
            db.session.delete(post_to_delete)
            db.session.commit()
            flash('Post Deleted Successfully')
            posts = Posts.query.order_by(Posts.date_posted)
            return render_template('posts.html', posts=posts)
        except:
            flash('Issue occurred while deleting the post')
            posts = Posts.query.order_by(Posts.date_posted)
            return render_template('posts.html', posts=posts)
    else:
        flash('You are not authorized to delete this post')
        posts = Posts.query.order_by(Posts.date_posted)
        return render_template('posts.html', posts=posts)

# Create Login
@app.route('/login', methods = ['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username = form.username.data).first()
        if user and user.verify_password(form.password.data):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password')
    return render_template('login.html', form = form)

# Create Dashboard 
@login_required
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    form = UserForm()
    id = current_user.id
    name_to_update = Users.query.get_or_404(id)
    if request.method == 'POST':
        name_to_update.name = request.form.get('name', name_to_update.name)
        name_to_update.email = request.form.get('email', name_to_update.email)
        name_to_update.username = request.form.get('username', name_to_update.username)
        password = request.form.get('password_hash')
        if password:
            name_to_update.password_hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)

        try:
            db.session.commit()
            flash('Updated Successfully!')
            return render_template('dashboard.html', form=form, name_to_update=name_to_update)
        except:
            flash('Errrr.. Looks like there was a problem!')
            return render_template('dashboard.html', form=form, name_to_update=name_to_update)
    else:
        return render_template('dashboard.html', form=form, name_to_update=name_to_update)

# Create logout function 
@login_required
@app.route('/logout', methods = ['GET', 'POST'])
def logout():
	logout_user()
	flash('You have been logged out Successfully')
	return redirect(url_for('login'))

# Create Search Function
@app.route('/search', methods=["POST"])
def search():
    form = SearchForm()
    posts = Posts.query
    searched = None
    if form.validate_on_submit():
        # Get data from submitted form
        searched = form.searched.data
        # Query the Database
        posts = posts.filter(Posts.content.like('%' + searched + '%'))
        posts = posts.order_by(Posts.title).all()
    return render_template("search.html", form=form, searched=searched, posts=posts)

# Passing to navbar
@app.context_processor
def base():
	form = SearchForm()
	return dict(form=form)