from flask import Flask,request,render_template,redirect,url_for,session,flash
from flask_sqlalchemy import SQLAlchemy
from hashutils import make_pw_hash,check_pw_hash
from datetime import datetime,time, date
from flask_login import LoginManager,UserMixin,login_user,current_user,logout_user,login_required



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:password@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO']= True
db = SQLAlchemy(app)
app.secret_key ='secretkey'
login_manager = LoginManager(app)
login_manager.login_view = 'login'


class User(db.Model,UserMixin):
    id = db.Column(db.Integer,primary_key=True)
    email = db.Column(db.String(120), unique=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Post', backref='owner')

    def __init__(self,email,password,username):

        self.email = email
        self.username = username
        self.password = make_pw_hash(password)

class Post(db.Model):
    users = db.relationship(User)
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'),nullable=False)
    blog_title = db.Column(db.String(120))
    blog_post = db.Column(db.Text,nullable=False)
    date_published = db.Column(db.DateTime,nullable=False, default=datetime.now)

    def __init__(self, blog_title, blog_post, owner):
        self.blog_title = blog_title
        self.blog_post = blog_post
        self.owner = owner
        

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def index():
    # page =request.args.get('page',1,type=int)
    users = User.query.order_by(User.username.asc()).all()
    # .paginate(page=page,per_page=3)
    return render_template('/index.html',users=users)
    
@app.route('/login', methods=['POST','GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('display_blogs'))
    
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email =email).first()

        if user and check_pw_hash(password,user.password):
             #Remember that user has logged in
            login_user(user)
            flash('User Logged in','success')
        
            return redirect(url_for('display_blogs'))
        else:
            flash('user password incorrect ,or user does not exist','danger')
            #Expalain why the login Failed

    return render_template('login.html')



@app.route('/signup',methods=['POST','GET'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        username = request.form['username']
        verify_password = request.form['verify_password']
    
        username_error = ''
        email_error = ''
        password_error = ''
        verify_password_error = ''

    #Username Validation

        if username == '':
            username_error ="Please Enter Username"
        elif not username.isalnum():
            username_error = "The username cannot contain any special characters"
        
        
        elif len(username) < 3:
            username_error = "Your Username cannot be less that 3 characters"
        elif len(username) > 20:
            username_error = "Your Username cannot be more that 20 characters"
        elif ' ' in username:
            username_error = "Username cannot contain any space"
    #End Of  username Validation

    #Email Validation

        if email != '':
            if "@" not in email:
                email_error="Email Address must include @"
        
            
            elif "." not in email:
                email_error = "Email must include a Periode(.)"
            elif ' ' in email:
                email_error ="Email cannot include any space"

        
    #End of email validation

    #Password Validation
        if password == '':
            password_error ="Password must be entered"
        elif len(password) < 3:
            password_error ="Password cannot be less than 2 characters"
        elif len(password) > 20:
            password_error ="Password cannot be more than 20 characters"
        elif " " in password:
            password_error =" Password cannot contains any space"
        if not password_error:
            if verify_password =="":
                verify_password_error = "Please enter a password"
            elif verify_password != password:
                verify_password_error ="Password Does not match"
        
        if not username_error and not email_error and not password_error and not verify_password_error:
            existing_user = User.query.filter_by(email=email,username=username).first()
            if not existing_user:
                new_user = User(email,password,username)
                db.session.add(new_user)
                db.session.commit()
                flash(f'your account has been created{username}', 'success')
                return redirect('/login')
            else:
                flash("This username or email is already registerned",'danger')
                return render_template('signup.html')
        else:
            return render_template('signup.html',username_error=username_error
                              ,email_error=email_error,password_error=password_error,
                              verify_password_error=verify_password_error)
    else:
        return render_template('signup.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

    

@app.route('/blog')
def display_blogs():
    # page =request.args.get('page',1,type=int)
    posts = Post.query.order_by(Post.date_published.desc())
    # .paginate(page=page,per_page=3)
    return render_template('blog.html',posts=posts)

        

@app.route('/newpost', methods=['GET','POST'])
@login_required
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
            new_post =Post(blog_title,blog_post,owner=current_user)
            db.session.add(new_post)
            db.session.commit()
            return redirect(url_for('display_blogs'))
        else:
            return render_template('newpost.html',blog_title_error=blog_title_error, 
            blog_post_error=blog_post_error)
    else:
        return render_template('newpost.html')





@app.route("/post/<int:post_id>")
def single_post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('single-post.html', post=post)


@app.route("/<username>")
def single_user(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(owner=user).order_by(Post.date_published.desc())
    post_number = Post.query.filter_by(owner=user).count()
     # .paginate(page=page,per_page=3)
    return render_template('singleUser.html', posts= posts,user=user,post_number = post_number)







if __name__ == "__main__":
    app.run(debug=True)


