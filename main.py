from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:launchcode@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'motlHS9jk2iu05asl0l'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1200))
    owner_id =db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

    def __repr__(self):
        return '<Blog %r>' % self.title

    def is_valid(self):
        if self.title and self.body:
            return True
        else:
            return False

class User(db.Model):

    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(50))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __repr__(self):
        return '<User %r>' % self.username

@app.before_request
def require_login():
    allowed_routes = ['login', 'display_blog_posts', 'index', 'signup']
    if request.endpoint not in allowed_routes and 'user' not in session:
        return redirect("/login")

@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', title="Home", users=users)

@app.route("/blog")
def display_blog_posts():

    if "user" in request.args:
        user_id = request.args.get("user")
        user = User.query.get(user_id)
        user_blogs = Blog.query.filter_by(owner=user).all()
        return render_template('user_posts.html', title="User Posts", user=user, user_blogs=user_blogs)

    blog_id = request.args.get('id')
    if (blog_id):
        blog = Blog.query.get(blog_id)
        return render_template('single_post.html', title="Blog Post", blog=blog)

    all_blogs = Blog.query.all()
    return render_template('all_posts.html', title="All Blogs", all_blogs=all_blogs)    

@app.route("/newpost", methods=['POST', 'GET'])
def new_post():
    
    if request.method == 'POST':
        owner = User.query.filter_by(username=session['user']).first()
        new_blog_title = request.form['title']
        new_blog_body = request.form['body']
        new_blog = Blog(new_blog_title, new_blog_body, owner)

        if new_blog.is_valid():
            db.session.add(new_blog)
            db.session.commit()
            url = "/blog?id="+str(new_blog.id)
            return redirect(url)
        else:
            flash("You need both a title and a body. Please check blog for errors")
            return render_template('newpost.html',
                title="Create new blog post",
                new_blog_title=new_blog_title,
                new_blog_body=new_blog_body)

    else:
        return render_template('newpost.html', title="Create new blog post")
            
@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users = User.query.filter_by(username=username)
        if users.count() == 0:
            flash("Username does not exist.")
            return redirect('/login')
        user = users.first()
        if password != user.password:
            flash("Password incorrect, please try again")
            return redirect('/login')
        session['user'] = user.username
        flash('Welcome back, '+user.username)
        return redirect("/newpost")
    else:
        return render_template('login.html', title="Login")

@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        if username == '':
            flash("Please enter a username.")
            return redirect("/signup")
        if password == '':
            flash("Please enter a password.")
            return redirect("/signup")
        if verify == '':
            flash("Please verify your password")
            return redirect("/signup")
        if len(username) < 3:
            flash("Invalid username, not long enough, please try again.")
            return redirect('/signup')
        if len(password) < 3:
            flash("Invalid password, not long enough, please try again.")
            return redirect('/signup')
        username_db_count = User.query.filter_by(username=username).count()
        if username_db_count > 0:
            flash(username + 'is already taken and password reminders are not implemented')
            return redirect('/signup')
        if password != verify:
            flash('Passwords did not match.')
            return redirect('/signup')
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        session['user'] = user.username
        return redirect("/newpost")
    else:
        return render_template('signup.html', title="Signup")

@app.route("/logout", methods=['POST'])
def logout():
    del session['user']
    return redirect("/blog")

if __name__ == '__main__':
    app.run()