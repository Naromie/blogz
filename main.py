from flask import Flask,request,render_template,redirect,url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:Reginaro@153@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO']= True
db = SQLAlchemy(app)

class Post(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    blog_title = db.Column(db.String(120))
    blog_post = db.Column(db.String(1100))

    def __init__(self,blog_title, blog_post):
        self.blog_title = blog_title
        self.blog_post = blog_post


@app.route('/blog')

def display_blogs():
    posts =Post.query.all()
    return render_template('blog.html',posts=posts)


@app.route('/newpost', methods=['GET','POST'])
def add_new_post():
    if request.method =='POST':
        blog_title = request.form['blog_title']
        blog_post = request.form['blog_post']

        blog_title_error =''
        blog_post_error =''

        if blog_title == '':
            blog_title_error="You must enter a Blog Title"
        if blog_post == '':
            blog_post_error ="Please type your blog post"

        if not blog_title_error and not blog_post_error:
            new_post =Post(blog_title,blog_post)
            db.session.add(new_post)
            db.session.commit()
            return redirect(url_for('display_blogs'))
        else:
            return render_template('newpost.html',blog_title_error=blog_title_error, 
            blog_post_error=blog_post_error)
    else:
        return render_template('newpost.html')


@app.route("/post/<int:post_id>")
def post(post_id):
    post =Post.query.get_or_404(post_id)
    return render_template('single-post.html', post=post)




if __name__ == "__main__":
    app.run(debug=True)


