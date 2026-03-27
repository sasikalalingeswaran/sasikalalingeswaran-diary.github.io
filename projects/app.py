from flask import Flask, redirect, render_template, session, request
from model import db, diary_login,Diary
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from sqlalchemy.exc import IntegrityError
import re

app = Flask(__name__)
app.secret_key = "something_12345"
bcrypt=Bcrypt(app)

app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:Krishnapriya22@localhost/my_diary"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app,db)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/diary')
def diary():
    if 'loggedin' not in session:
        return redirect('/login')
    user_id = session['id']
    entries = Diary.query.filter_by(user_id=user_id).all()
    return render_template('diary.html', entries=entries,username=session["username"],email=session.get('email'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        account = diary_login.query.filter_by(username=username).first()
        if account and bcrypt.check_password_hash(account.password,password):
            session['loggedin'] = True
            session['id'] = account.id
            session['username'] = account.username
            session['password']=account.password
            session['email'] = account.email 
            return redirect('/diary')
        else:
            msg = 'Username does not exists! '
    return render_template('login.html', msg=msg)

@app.route('/register',methods=['GET','POST'])
def register():
    failure=''
    user_error=''
    pass_error=''
    msg=''
    if request.method=='POST':
        username=request.form['username']
        user_pattern=r'^.{8,}$'
        if not re.search(user_pattern,username):
            user_error="*Username must contain 8 characters"
        password=request.form['password']
        pass_pattern=r'[!@#$%&]'
        if not re.search(pass_pattern,password):
            pass_error="*Password must contain one special character "
        if not user_error and not pass_error:
            hashed_password=bcrypt.generate_password_hash(password).decode('UTF-8')
            email=request.form['email']
            session['email']=email
            new_user=diary_login(username=username,password=hashed_password,email=email)
            try:
                db.session.add(new_user)
                db.session.commit()
                msg="Registered Successfully!"
            except IntegrityError:
                db.session.rollback()
                failure='Username or email already exists!'
    return render_template('register.html',msg=msg,user_error=user_error,pass_error=pass_error,failure=failure)

@app.route('/add',methods=["GET","POST"])
def add():
    if request.method=="POST":
        date=request.form["date"]
        textarea=request.form["textarea"]
        positive=["happy","not sad","cheerful","good","excited","glad","nice"]
        negative=["sad","not happy","not cheerful","not good","not excited","not feeling good","low","heavy","hard"]
        is_positive=any(word in textarea for word in positive)
        is_negative=any(word in textarea for word in negative)
        if is_positive and is_negative:
            mood="Neutral"
        elif is_negative:
            mood="Sad Mood"
        elif is_positive:
            mood="Happy mood"
        else:
            mood="Neutral"
        new_entry=Diary(date_entry=date,text_area=textarea,mood=mood,user_id = session['id'])
        db.session.add(new_entry)
        db.session.commit()
        return redirect('/diary')
    return redirect('/diary')

@app.route('/edit/<int:id>',methods=["GET","POST"])
def edit(id):
    new_data=Diary.query.get(id)
    if request.method=="POST":
        new_data.date_entry=request.form["date"]
        new_data.text_area=request.form["textarea"]
        db.session.commit()
        return redirect('/diary')
    
@app.route('/delete/<int:id>')
def delete(id):
    data=Diary.query.get(id)
    db.session.delete(data)
    db.session.commit()
    return redirect('/diary')

@app.route('/logout')
def logout():
    session.clear()
    return render_template('index.html')

if __name__ == "__main__":
    app.run()

