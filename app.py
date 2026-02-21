
from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = "rentcircle_secret_key"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rent_circle.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# -------------------- DATABASE MODELS --------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price_per_day = db.Column(db.Float, nullable=False)
    available_date = db.Column(db.Date, nullable=False)
    is_borrowed = db.Column(db.Boolean, default=False)

# -------------------- ROUTES --------------------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("User already registered! Please login.")
            return redirect(url_for('login'))

        new_user = User(email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful! Please login.")
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email, password=password).first()
        if user:
            session['user'] = user.email
            return redirect(url_for('main'))
        else:
            flash("Invalid email or password")

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/main')
def main():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('main.html')

@app.route('/borrowing')
def borrowing():
    today = datetime.today().date()
    tomorrow = today + timedelta(days=1)

    today_items = Item.query.filter_by(available_date=today, is_borrowed=False).all()
    tomorrow_items = Item.query.filter_by(available_date=tomorrow, is_borrowed=False).all()

    return render_template('borrowing.html',
                           today_items=today_items,
                           tomorrow_items=tomorrow_items)

@app.route('/borrow/<int:item_id>')
def borrow_item(item_id):
    if 'user' not in session:
        return redirect(url_for('login'))

    item = Item.query.get_or_404(item_id)
    item.is_borrowed = True
    db.session.commit()

    flash("Item borrowed successfully!")
    return redirect(url_for('borrowing'))

@app.route('/lending', methods=['GET', 'POST'])
def lending():
    if 'user' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        availability = request.form['availability']

        if availability == "today":
            available_date = datetime.today().date()
        else:
            available_date = datetime.today().date() + timedelta(days=1)

        new_item = Item(
            name=name,
            price_per_day=price,
            available_date=available_date,
            is_borrowed=False
        )
        db.session.add(new_item)
        db.session.commit()

        flash("Item added successfully!")
        return redirect(url_for('borrowing'))

    return render_template('lending.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
