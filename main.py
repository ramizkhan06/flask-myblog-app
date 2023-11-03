from flask import Flask, render_template, flash, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, EqualTo
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_migrate import Migrate 
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_ckeditor import CKEditor, CKEditorField


# Create a Flask Instance
app = Flask(__name__)
# Add CKEditor
ckeditor = CKEditor(app)
# Secret Key
app.config['SECRET_KEY'] = 'remix'
# Add Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

# Initialize the Database
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Flask Login Stuff
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

# User Models
class Users(db.Model, UserMixin):
	id = db.Column(db.Integer, primary_key = True)
	name = db.Column(db.String(30), nullable = False)
	email = db.Column(db.String(50), nullable = False, unique = True)
	username = db.Column(db.String(30))
	date_added = db.Column(db.DateTime, default = datetime.utcnow)
	# Adding Password Column
	password_hash = db.Column(db.String(20))
	# User can have many posts
	posts = db.relationship('Posts', backref='poster')

	@property
	def password(self):
		raise AttributeError('Password is not a readable attribute!')

	@password.setter
	def password(self, password):
		self.password_hash = generate_password_hash(password)

	def verify_password(self, password):
		return check_password_hash(self.password_hash, password)

	# Create a String
	def __repr__(self):
		return '<Name %r>' % self.name

# Blog Post Model
class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    slug = db.Column(db.String(255))
    # Foreign Key to link with Users
    poster_id = db.Column(db.Integer, db.ForeignKey('users.id'))

class UserForm(FlaskForm):
	name = StringField('Name', validators = [DataRequired()])
	username = StringField('Username', validators = [DataRequired()])
	email = StringField('Email', validators = [DataRequired()])
	submit = SubmitField('Submit')
	password_hash = PasswordField('Password', validators = [DataRequired(), EqualTo('password_hash2', message='Passwords must match')])
	password_hash2 = PasswordField('Confirm Password', validators = [DataRequired()])

# Create Post Form
class PostForm(FlaskForm):
	title = StringField('Title', validators = [DataRequired()])
	# content = StringField('Content', validators = [DataRequired()], widget = TextArea())
	content = CKEditorField('Content', validators = [DataRequired()])
	author = StringField('Author')
	slug = StringField('Topic', validators = [DataRequired()])
	submit = SubmitField('Submit')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Submit')

class SearchForm(FlaskForm):
	searched = StringField("Searched", validators=[DataRequired()])
	submit = SubmitField("Submit")

# Create a route decorator
@app.route('/')
def index():
	return render_template('index.html')

@app.route('/user/<name>')
def user(name):
	return render_template('user.html', name=name)

# Create custom error page
# Invalid error
@app.errorhandler(404)
def page_not_found(e):
	return render_template('404.html'), 404

# Internal server error
@app.errorhandler(500)
def page_not_found(e):
	return render_template('500.html'), 500

# Add User
@app.route('/user/add', methods=['GET', 'POST'])
def add_user():
    name = None
    form = UserForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            # Hash Password
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

# Update Database Record
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

@app.route('/posts')
def posts():
	# Getting all the post from database
	posts = Posts.query.order_by(Posts.date_posted)
	return render_template('posts.html', posts=posts)

@app.route('/posts/<int:id>')
def post(id):
	post = Posts.query.get_or_404(id)
	return render_template('post.html', post = post)

@login_required
@app.route('/posts/edit/<int:id>', methods=['GET', 'POST'])
def edit_post(id):
	post = Posts.query.get_or_404(id)
	form = PostForm()
	if form.validate_on_submit():
		post.title = form.title.data
		#post.author = form.author.data
		post.slug = form.slug.data
		post.content = form.content.data
		# Update Database
		db.session.add(post)
		db.session.commit()
		flash("Post Has Been Updated!")
		return redirect(url_for('post', id=post.id))
	
	if current_user.id == post.poster_id or current_user.id == 14:
		form.title.data = post.title
		#form.author.data = post.author
		form.slug.data = post.slug
		form.content.data = post.content
		return render_template('edit_post.html', form=form)
	else:
		flash("You Aren't Authorized To Edit This Post...")
		posts = Posts.query.order_by(Posts.date_posted)
		return render_template("posts.html", posts=posts)

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

# Create Dashboard page
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

# passing to navbar
@app.context_processor
def base():
	form = SearchForm()
	return dict(form=form)
