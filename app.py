import os
import sys
from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'yappy_compressor_secret_key_2024'

# Database configuration
basedir = os.path.abspath(os.path.dirname(__file__))

# Use /tmp/ for Render, local folder for development
if os.environ.get('RENDER'):
    db_path = os.path.join('/tmp', 'yappy.db')
else:
    db_path = os.path.join(basedir, 'yappy.db')

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    orders = db.relationship('Order', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Compressor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(20), default='unit')
    image_file = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    compressor_id = db.Column(db.Integer, db.ForeignKey('compressor.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default='Processing')
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    compressor = db.relationship('Compressor')

def renumber_orders(user_id):
    orders = Order.query.filter_by(user_id=user_id).order_by(Order.order_date).all()
    for index, order in enumerate(orders, 1):
        order.order_number = index
    db.session.commit()

def init_products():
    try:
        if Compressor.query.count() == 0:
            products = [
                Compressor(name='Compressor', category='Compressor', price=1288.00, unit='unit',
                          image_file='Compressor.web_p',
                          description='High-quality air conditioning compressor for efficient cooling performance.'),
                Compressor(name='R32 Refrigerant', category='Refrigerant', price=50.00, unit='per kg',
                          image_file='R32_Refrigerant.png',
                          description='Environmentally friendly R32 refrigerant gas.'),
                Compressor(name='Aircon Pipes', category='Pipes', price=28.00, unit='per metre',
                          image_file='Aircon_Pipes.avif',
                          description='Premium copper pipes for air conditioning installation.'),
                Compressor(name='Cooling Coil', category='Coils', price=688.00, unit='unit',
                          image_file='Cooling_Coil.png',
                          description='Efficient cooling coil for heat exchange systems.'),
                Compressor(name='Bearing', category='Bearings', price=128.00, unit='unit',
                          image_file='Bearing.jpg',
                          description='High-durability bearings for smooth compressor operation.'),
                Compressor(name='Screws Bolts', category='Hardware', price=28.00, unit='per box',
                          image_file='Screws & Bolts.webp',
                          description='Complete set of high-quality screws and bolts.'),
                Compressor(name='Nuts', category='Hardware', price=28.00, unit='per box',
                          image_file='akU5h7cfJ2TxNut_s_(per box).jpeg',
                          description='Premium quality nuts for secure fastening.'),
                Compressor(name='Serpentine Belt', category='Belts', price=188.00, unit='unit',
                          image_file='Serpentine_Belt.jpg',
                          description='Durable serpentine belt for compressor drive systems.'),
                Compressor(name='Manifold Gauge Sets', category='Tools', price=288.00, unit='set',
                          image_file='Manifold_Gauge_Set.jpg',
                          description='Professional manifold gauge set for AC maintenance and repair.'),
                Compressor(name='Expansion Valves', category='Valves', price=48.00, unit='unit',
                          image_file='Expansion_Valve.jpg',
                          description='Precision expansion valve for refrigerant flow control.'),
            ]
            db.session.add_all(products)
            db.session.commit()
            print(f"✅ Added {len(products)} products to database")
        else:
            print(f"Products already exist: {Compressor.query.count()} products")
    except Exception as e:
        print(f"❌ Error initializing products: {e}")

# Routes
@app.route('/')
def index():
    try:
        products = Compressor.query.all()
        categories = {}
        for product in products:
            if product.category not in categories:
                categories[product.category] = []
            categories[product.category].append(product)
        return render_template('index.html', categories=categories)
    except Exception as e:
        print(f"❌ Index error: {e}")
        return f"Error: {e}", 500

@app.route('/company')
def company():
    try:
        return render_template('company.html')
    except Exception as e:
        print(f"❌ Company page error: {e}")
        return f"Error: {e}", 500

@app.route('/register', methods=['GET', 'POST'])
def register():
    try:
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            
            if User.query.filter_by(username=username).first():
                return render_template('register.html', error='Username already exists')
            
            user = User(username=username)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            
            return redirect(url_for('login'))
        
        return render_template('register.html')
    except Exception as e:
        print(f"❌ Register error: {e}")
        return f"Error: {e}", 500

@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            
            user = User.query.filter_by(username=username).first()
            if user and user.check_password(password):
                session['user_id'] = user.id
                session['username'] = user.username
                return redirect(url_for('index'))
            
            return render_template('login.html', error='Invalid username or password')
        
        return render_template('login.html')
    except Exception as e:
        print(f"❌ Login error: {e}")
        return f"Error: {e}", 500

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/order/<int:product_id>')
def order(product_id):
    try:
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        product = Compressor.query.get_or_404(product_id)
        return render_template('order.html', product=product)
    except Exception as e:
        print(f"❌ Order error: {e}")
        return f"Error: {e}", 500

@app.route('/place_order/<int:product_id>', methods=['POST'])
def place_order(product_id):
    try:
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        quantity = int(request.form.get('quantity', 1))
        product = Compressor.query.get_or_404(product_id)
        total_price = product.price * quantity
        
        user_orders = Order.query.filter_by(user_id=session['user_id']).all()
        next_order_number = len(user_orders) + 1
        
        order = Order(
            user_id=session['user_id'],
            compressor_id=product_id,
            quantity=quantity,
            total_price=total_price,
            order_number=next_order_number,
            status='Processing'
        )
        db.session.add(order)
        db.session.commit()
        
        return redirect(url_for('track'))
    except Exception as e:
        print(f"❌ Place order error: {e}")
        return f"Error: {e}", 500

@app.route('/remove_order/<int:order_id>', methods=['POST'])
def remove_order(order_id):
    try:
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        order = Order.query.get_or_404(order_id)
        
        if order.user_id != session['user_id']:
            return redirect(url_for('track'))
        
        if order.status != 'Completed':
            db.session.delete(order)
            db.session.commit()
            renumber_orders(session['user_id'])
        
        return redirect(url_for('track'))
    except Exception as e:
        print(f"❌ Remove order error: {e}")
        return f"Error: {e}", 500

@app.route('/track')
def track():
    try:
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        orders = Order.query.filter_by(user_id=session['user_id']).order_by(Order.order_number).all()
        return render_template('track.html', orders=orders)
    except Exception as e:
        print(f"❌ Track error: {e}")
        return f"Error: {e}", 500

# Create necessary directories
def setup_static_files():
    try:
        os.makedirs(os.path.join(basedir, 'static', 'images'), exist_ok=True)
        os.makedirs(os.path.join(basedir, 'static', 'css'), exist_ok=True)
        print("✅ Static directories created")
    except Exception as e:
        print(f"❌ Error creating static directories: {e}")

# Initialize database when app starts
print("🚀 Starting Yappy Compressor application...")
print(f"📁 Database path: {app.config['SQLALCHEMY_DATABASE_URI']}")

with app.app_context():
    try:
        print("📊 Creating database tables...")
        db.create_all()
        print("✅ Database tables created/verified")
        
        print("📦 Initializing products...")
        init_products()
        
        print("📁 Setting up static files...")
        setup_static_files()
        
        print("✅ App initialization complete!")
    except Exception as e:
        print(f"❌ FATAL: Could not initialize database: {e}")
        sys.stderr.write(f"FATAL: {e}\n")

# For local development
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)