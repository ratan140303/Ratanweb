from flask import Flask, render_template, redirect, request, flash, session, url_for
from flask_sqlalchemy import SQLAlchemy
import bcrypt


app = Flask(__name__)

# Make Connection with Data Base
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.secret_key = 'Bablu@12345'

db = SQLAlchemy(app)




# Create Database with the name of "User"
class User(db.Model): 
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

    def __init__(self, email, password, name):
        self.name = name
        self.email = email
        self.password = self.hash_password(password)

    def hash_password(self, password):
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))
 
# Create Database with the name of "User"
class Contactus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    message = db.Column(db.String(200))

    def __init__(self, name, email, message):
        self.name = name
        self.email = email
        self.message = message

with app.app_context():
    db.create_all()

# Home Page 
@app.route('/home')
@app.route('/')
def index():
    return render_template('home.html', title='Home', current_page='home')


# Register Page 
@app.route('/signup', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already exists. Please use different email.', 'error')
            return redirect('/signup')  # Redirect back to registration page with flash message
    
        new_user = User(name=name, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful. Please log in.', 'success')
        return redirect('/signup')

    return render_template('signup.html')


# Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session['email'] = user.email
            return redirect('/dashboard')
        else:
            error = 'Invalid email or password. Please try again.'
            flash(error, 'error')

    return render_template('login.html')

#Dashboard
@app.route('/dashboard')
def dashboard():
    if 'email' in session:
        return render_template('dashboard.html', title='Dashboard', current_page='dashboard')
    else:
        flash('You need to login first.', 'error')
        return redirect('/login')

#About Page
@app.route('/about')
def about():
    return render_template('about.html', title='About', current_page='about')
   
#ContactUs Page
@app.route('/contactus', methods=['GET', 'POST'])
def contactus():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']

        new_contact = Contactus(name=name, email=email, message=message)
        db.session.add(new_contact)
        db.session.commit()
        flash('Message Sent Successfully.', 'success')
        return redirect('/contactus')
    return render_template('contactus.html', title='Contact Us', current_page='contactus')


#Logout Page
@app.route('/logout')
def logout():
    session.pop('email', None)
    flash('You have been logged out.', 'info')
    return redirect('/login')


if __name__ == '__main__':
    app.run(debug=True)