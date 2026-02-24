from flask import Flask, redirect, render_template, session, request
from model import db, diary_login,Diary
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from sqlalchemy.exc import IntegrityError

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
    if request.method=='POST':
        username=request.form['username']
        password=request.form['password']
        hashed_password=bcrypt.generate_password_hash(password).decode('UTF-8')
        email=request.form['email']
        session['email']=email
        new_user=diary_login(username=username,password=hashed_password,email=email)
        try:
            db.session.add(new_user)
            db.session.commit()
            msg="Registered Successfully!"
            return render_template('register.html',msg=msg)
        except IntegrityError:
            db.session.rollback()
            failure='Username already exists!'
        return render_template('register.html',failure=failure)
    return render_template('register.html')

@app.route('/add',methods=["GET","POST"])
def add():
    if request.method=="POST":
        date=request.form["date"]
        textarea=request.form["textarea"]
        if 'happy' in textarea.lower() or 'excited' in textarea.lower():
            mood='Happy'
        elif 'sad' in textarea or 'not happy' in textarea or 'bad' in textarea.lower():
            mood='Sad'
        else:
            mood='Neutral'
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


