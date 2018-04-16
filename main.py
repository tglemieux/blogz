from flask import Flask, request, redirect, render_template, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:launchcode@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'fm99jk2iu05asl0l'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1200))

    def __init__(self, title, body):
        self.title = title
        self.body = body

    def is_valid(self):
        if self.title and self.body:
            return True
        else:
            return False


@app.route('/')
def index():
    return redirect("/blog")

@app.route("/blog")
def display_blog_posts():

    blog_id = request.args.get('id')
    if (blog_id):
        blog = Blog.query.get(blog_id)
        return render_template('single_post.html', title="Blog Post", blog=blog)

    all_blogs = Blog.query.all()
    return render_template('all_posts.html', title="All Blogs", all_blogs=all_blogs)    

@app.route("/newpost", methods=['POST', 'GET'])
def new_post():
    
    if request.method == 'POST':
        new_blog_title = request.form['title']
        new_blog_body = request.form['body']
        new_blog = Blog(new_blog_title, new_blog_body)

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
            

if __name__ == '__main__':
    app.run()