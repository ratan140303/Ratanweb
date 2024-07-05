from flask import Flask, render_template, redirect, request, flash, session, url_for
from flask_sqlalchemy import SQLAlchemy
import bcrypt
import datetime


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
    
class MillData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, default=datetime.datetime.now)
    #Credits
    mill_credit = db.Column(db.Integer, nullable=False)
    
    flour_weight = db.Column(db.Integer, nullable=False)
    flour_rs = db.Column(db.Integer, nullable=False)
    
    oil_weight = db.Column(db.Integer, nullable=False)
    oil_rs = db.Column(db.Integer, nullable=False)
    
    khari_weight = db.Column(db.Integer, nullable=False)
    khari_rs = db.Column(db.Integer, nullable=False)

    # Debits
    labour_dscri = db.Column(db.String(100), nullable=False)
    labour_rs = db.Column(db.Integer, nullable=False)

    mill_debit = db.Column(db.Integer, nullable=False)
    mill_dscri = db.Column(db.String(100), nullable=False)

    home_debit = db.Column(db.Integer, nullable=False)
    home_dscri = db.Column(db.String(100), nullable=False)

    gehum_weight = db.Column(db.Integer, nullable=False)
    gehum_rs = db.Column(db.Integer, nullable=False)

    # Total
    total_credit = db.Column(db.Integer, nullable=False)
    total_debit = db.Column(db.Integer, nullable=False)
    user = db.relationship('User', backref=db.backref('milldatas', lazy=True))

    def __init__(self, user_id, mill_credit, flour_weight, flour_rs, oil_weight, oil_rs, khari_weight, khari_rs, labour_dscri, labour_rs, mill_debit, mill_dscri, home_debit, home_dscri, gehum_weight, gehum_rs):
        self.user_id = user_id
        self.mill_credit = mill_credit
        self.flour_weight = flour_weight
        self.flour_rs = flour_rs
        self.oil_weight = oil_weight
        self.oil_rs = oil_rs
        self.khari_weight = khari_weight
        self.khari_rs = khari_rs
        self.labour_dscri = labour_dscri
        self.labour_rs = labour_rs
        self.mill_debit = mill_debit
        self.mill_dscri = mill_dscri
        self.home_debit = home_debit
        self.home_dscri = home_dscri
        self.gehum_weight = gehum_weight
        self.gehum_rs = gehum_rs
        self.total_credit = int(mill_credit) + int(flour_rs) + int(oil_rs) + int(khari_rs)
        self.total_debit = int(mill_debit) + int(home_debit) + int(gehum_rs) + int(labour_rs)
 
# Create Database for contact us
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
        # Check if there's already a user registered
        existing_users = User.query.count()
        if existing_users >= 2:
            flash('Registration is closed. Only two user is allowed to the website', 'error')
            return redirect('/login')

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
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'email' in session:
        user = User.query.filter_by(email=session['email']).first()

        year = datetime.datetime.now().year # Give: 2024/2023..
        current_year = datetime.datetime.now().year # Give: 2024/2023..
        month = datetime.datetime.now().month # Give: 1/2/3/4/5..
        month_name = datetime.datetime.now().strftime("%B")

        if request.method == 'POST':
            year = request.form['year']
            month = request.form['month']

            year = int(year)
            month = int(month)
            month_name = datetime.datetime(year, month, 1).strftime("%B")

            mill_dairy_datas = MillData.query.filter(
            MillData.user_id == user.id,
            db.extract('year', MillData.date) == year,
            db.extract('month', MillData.date) == month
            ).all()
        else:
            mill_dairy_datas = MillData.query.filter(
            MillData.user_id == user.id,
            db.extract('year', MillData.date) == year,
            db.extract('month', MillData.date) == month
            ).all()


        # Calculate totals
        total_t_credit = sum(data.total_credit for data in mill_dairy_datas)
        total_t_debit = sum(data.total_debit for data in mill_dairy_datas)
        total_m_credit = sum(data.mill_credit for data in mill_dairy_datas)
        total_flour_rs = sum(data.flour_rs for data in mill_dairy_datas)
        total_flour_weight = sum(data.flour_weight for data in mill_dairy_datas)
        total_oil_rs = sum(data.oil_rs for data in mill_dairy_datas)
        total_oil_weight = sum(data.oil_weight for data in mill_dairy_datas)
        total_khari_rs = sum(data.khari_rs for data in mill_dairy_datas)
        total_khari_weight = sum(data.khari_weight for data in mill_dairy_datas)
        total_mill_debit = sum(data.mill_debit for data in mill_dairy_datas)
        total_home_debit = sum(data.home_debit for data in mill_dairy_datas)
        total_labour_rs = sum(data.labour_rs for data in mill_dairy_datas)
        total_gehum_rs = sum(data.gehum_rs for data in mill_dairy_datas)
        total_gehum_weight = sum(data.gehum_weight for data in mill_dairy_datas)

        return render_template('dashboard.html', title='Dashboard', current_page='dashboard',
                               mill_dairy_datas=mill_dairy_datas, year=year, current_year=current_year,
                               month=month, month_name=month_name,
                               total_t_credit=total_t_credit, total_t_debit=total_t_debit,
                               total_m_credit=total_m_credit, total_flour_rs=total_flour_rs,
                               total_flour_weight=total_flour_weight, total_oil_rs=total_oil_rs,
                               total_oil_weight=total_oil_weight, total_khari_rs=total_khari_rs,
                               total_khari_weight=total_khari_weight, total_mill_debit=total_mill_debit,
                               total_home_debit=total_home_debit, total_labour_rs=total_labour_rs,
                               total_gehum_rs=total_gehum_rs, total_gehum_weight=total_gehum_weight)

        #return render_template('dashboard.html', title='Dashboard', current_page='dashboard', mill_dairy_datas=mill_dairy_datas, current_year=current_year, current_month=current_month)
    else:
        flash('You need to login first.', 'error')
        return redirect('/login')

#add_new_data
@app.route('/add_new_data', methods=['GET', 'POST'])
def add_new_data():
    if 'email' in session:
        user = User.query.filter_by(email=session['email']).first()
        if request.method == 'POST':
            mill_credit = request.form['m_credit']

            flour_weight = request.form['flour_weight']
            flour_rs = request.form['flour_rs']

            oil_weight = request.form['oil_weight']
            oil_rs = request.form['oil_rs']

            khari_weight = request.form['khari_weight']
            khari_rs = request.form['khari_rs']
            
            labour_dscri = request.form['labour_dscri']
            labour_rs = request.form['labour_rs']

            mill_debit = request.form['mill_debit']
            mill_dscri = request.form['mill_dscri']

            home_debit = request.form['home_debit']
            home_dscri = request.form['home_dscri']

            gehum_weight = request.form['gehum_weight']
            gehum_rs = request.form['gehum_rs']

            # Check if data for today already exists
            today = datetime.date.today()
            today_data = MillData.query.filter_by(user_id=user.id, date=today).first()
            if today_data:
                flash("Today's mill data already exists.", 'error')
                return redirect('/add_new_data')
            

            new_data = MillData(user_id=user.id, mill_credit=mill_credit, flour_weight=flour_weight, flour_rs=flour_rs, oil_weight=oil_weight, oil_rs=oil_rs, khari_weight=khari_weight, khari_rs=khari_rs, labour_dscri=labour_dscri, labour_rs=labour_rs, mill_debit=mill_debit, mill_dscri=mill_dscri, home_debit=home_debit, home_dscri=home_dscri, gehum_weight=gehum_weight, gehum_rs=gehum_rs)
            db.session.add(new_data)
            db.session.commit()
            flash('Added successful.', 'success')
            return redirect('/add_new_data')

        return render_template('add_new.html', title='Add data', current_page='dashboard')
    else:
        flash('You need to login first.', 'error')
        return redirect('/login')

@app.route('/edit_data/<int:data_id>', methods=['GET'])
def edit_data(data_id):
    if 'email' in session:
        user = User.query.filter_by(email=session['email']).first()
        mill_data = MillData.query.filter_by(id=data_id, user_id=user.id).first()
        
        if not mill_data:
            flash('Data not found or you do not have permission to edit this data.', 'error')
            return redirect('/dashboard')
        
        return render_template('edit_data.html', mill_data=mill_data)
    else:
        flash('You need to login first.', 'error')
        return redirect('/login')

@app.route('/update_data/<int:data_id>', methods=['POST'])
def update_data(data_id):
    if 'email' in session:
        user = User.query.filter_by(email=session['email']).first()
        mill_data = MillData.query.filter_by(id=data_id, user_id=user.id).first()
        
        if not mill_data:
            flash('Data not found or you do not have permission to edit this data.', 'error')
            return redirect('/dashboard')
        
        mill_data.mill_credit = request.form['m_credit']
        mill_data.flour_weight = request.form['flour_weight']
        mill_data.flour_rs = request.form['flour_rs']
        mill_data.oil_weight = request.form['oil_weight']
        mill_data.oil_rs = request.form['oil_rs']
        mill_data.khari_weight = request.form['khari_weight']
        mill_data.khari_rs = request.form['khari_rs']
        mill_data.labour_dscri = request.form['labour_dscri']
        mill_data.labour_rs = request.form['labour_rs']
        mill_data.mill_debit = request.form['mill_debit']
        mill_data.mill_dscri = request.form['mill_dscri']
        mill_data.home_debit = request.form['home_debit']
        mill_data.home_dscri = request.form['home_dscri']
        mill_data.gehum_weight = request.form['gehum_weight']
        mill_data.gehum_rs = request.form['gehum_rs']
        mill_data.total_credit = int(mill_data.mill_credit) + int(mill_data.flour_rs) + int(mill_data.oil_rs) + int(mill_data.khari_rs)
        mill_data.total_debit = int(mill_data.mill_debit) + int(mill_data.home_debit) + int(mill_data.gehum_rs) + int(mill_data.labour_rs)

        db.session.commit()
        flash('Data updated successfully.', 'success')
        return redirect('/dashboard')
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