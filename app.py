import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, g, copy_current_request_context
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect, generate_csrf
import shortuuid
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
import os
from dotenv import load_dotenv
from paypalcheckoutsdk.core import PayPalHttpClient, SandboxEnvironment, LiveEnvironment
from paypalcheckoutsdk.orders import OrdersCreateRequest, OrdersCaptureRequest

# Load environment variables
load_dotenv()

app = Flask(__name__)
# Generate a secure random secret key if not set in environment
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', os.urandom(24).hex())
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///payments.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size
app.config['WTF_CSRF_TIME_LIMIT'] = 3600  # 1 hour CSRF token expiration

# PayPal Configuration
PAYPAL_CLIENT_ID = os.getenv('PAYPAL_CLIENT_ID')
PAYPAL_SECRET = os.getenv('PAYPAL_SECRET')
PAYPAL_ENVIRONMENT = os.getenv('PAYPAL_ENVIRONMENT', 'sandbox')

class PayPalClient:
    def __init__(self):
        if not PAYPAL_CLIENT_ID or not PAYPAL_SECRET:
            error_msg = f"PayPal credentials are not properly configured. CLIENT_ID: {'SET' if PAYPAL_CLIENT_ID else 'MISSING'}, SECRET: {'SET' if PAYPAL_SECRET else 'MISSING'}"
            app.logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Validate credentials are not empty strings
        if len(PAYPAL_CLIENT_ID.strip()) == 0 or len(PAYPAL_SECRET.strip()) == 0:
            error_msg = "PayPal credentials are empty strings"
            app.logger.error(error_msg)
            raise ValueError(error_msg)
            
        try:
            if PAYPAL_ENVIRONMENT == 'sandbox':
                self.environment = SandboxEnvironment(
                    client_id=PAYPAL_CLIENT_ID,
                    client_secret=PAYPAL_SECRET
                )
                print(f"PayPal client initialized in {PAYPAL_ENVIRONMENT} mode")
                print(f"Client ID prefix: {PAYPAL_CLIENT_ID[:10]}...")
            else:
                self.environment = LiveEnvironment(
                    client_id=PAYPAL_CLIENT_ID,
                    client_secret=PAYPAL_SECRET
                )
                app.logger.info(f"PayPal client initialized in live mode")
                app.logger.info(f"Client ID prefix: {PAYPAL_CLIENT_ID[:10]}...")
                
            self.client = PayPalHttpClient(self.environment)
            
        except Exception as e:
            error_msg = f"Failed to initialize PayPal client: {str(e)}"
            app.logger.error(error_msg)
            raise ValueError(error_msg)

# Initialize PayPal client
try:
    paypal_client = PayPalClient()
except Exception as e:
    app.logger.critical(f"CRITICAL: Failed to initialize PayPal client on startup: {str(e)}")
    # Create a dummy client to prevent app crash, but log the error
    paypal_client = None

# Initialize extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)
csrf = CSRFProtect(app)

# Make CSRF token available in all templates
@app.context_processor
def inject_csrf_token():
    return dict(csrf_token=generate_csrf)

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Models
class PaymentLink(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)
    delivery_cost = db.Column(db.Float, default=0.0, nullable=False)
    client_name = db.Column(db.String(100), nullable=False)
    delivery_method = db.Column(db.String(50), nullable=False)
    unique_id = db.Column(db.String(20), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_paid = db.Column(db.Boolean, default=False, nullable=False)
    payment_id = db.Column(db.String(100), nullable=True)
    paid_at = db.Column(db.DateTime, nullable=True)
    
    @property
    def total_amount(self):
        return self.price + (self.delivery_cost or 0)

# Context processor to make current datetime available in all templates
@app.context_processor
def inject_now():
    return {'now': datetime.utcnow()}

def cleanup_old_links():
    """Delete payment links older than 24 hours"""
    expiration_time = datetime.utcnow() - timedelta(hours=24)
    old_links = PaymentLink.query.filter(PaymentLink.created_at < expiration_time).all()
    for link in old_links:
        db.session.delete(link)
    db.session.commit()
    return len(old_links)

# Test route to verify PayPal configuration (only for development)
@app.route('/test-paypal-config')
def test_paypal_config():
    # Only allow in development/sandbox mode for security
    if PAYPAL_ENVIRONMENT != 'sandbox':
        return jsonify({'error': 'This endpoint is only available in sandbox mode'}), 403
    
    return jsonify({
        'paypal_client_id': PAYPAL_CLIENT_ID[:10] + '...' if PAYPAL_CLIENT_ID else 'NOT SET',
        'paypal_secret': 'SET' if PAYPAL_SECRET else 'NOT SET',
        'paypal_environment': PAYPAL_ENVIRONMENT,
        'config_status': 'OK' if PAYPAL_CLIENT_ID and PAYPAL_SECRET else 'MISSING CREDENTIALS'
    })

# Health check endpoint for PayPal status
@app.route('/health/paypal')
def paypal_health():
    return jsonify({
        'paypal_initialized': paypal_client is not None,
        'paypal_environment': PAYPAL_ENVIRONMENT,
        'credentials_configured': PAYPAL_CLIENT_ID is not None and PAYPAL_SECRET is not None,
        'client_id_length': len(PAYPAL_CLIENT_ID) if PAYPAL_CLIENT_ID else 0,
        'status': 'OK' if paypal_client is not None else 'ERROR'
    })

# Routes
@app.route('/')
def index():
    # Clean up old links before showing the page
    deleted_count = cleanup_old_links()
    print(f"Deleted {deleted_count} old payment links")
    
    # Get recent links (last 10 created, not older than 1 hour)
    recent_links = PaymentLink.query.order_by(PaymentLink.created_at.desc()).limit(10).all()
    return render_template('index.html', recent_links=recent_links)

@app.route('/create_link', methods=['GET', 'POST'])
def create_link():
    if request.method == 'POST':
        product_name = request.form.get('product_name')
        price = float(request.form.get('price'))
        delivery_cost = float(request.form.get('delivery_cost', 0))
        client_name = request.form.get('client_name', 'Client')
        delivery_method = request.form.get('delivery_method')
        
        # Generate unique ID for the payment link
        unique_id = shortuuid.uuid()[:10]
        
        # Create new payment link
        new_link = PaymentLink(
            product_name=product_name,
            price=price,
            delivery_cost=delivery_cost,
            client_name=client_name,
            delivery_method=delivery_method,
            unique_id=unique_id
        )
        
        db.session.add(new_link)
        db.session.commit()
        
        # Generate the payment URL
        payment_url = url_for('payment_page', unique_id=unique_id, _external=True)
        
        return render_template('link_created.html', payment_url=payment_url)
    
    return render_template('create_link.html')

@app.route('/payment/<unique_id>', methods=['GET', 'POST'])
def payment_page(unique_id):
    payment_link = PaymentLink.query.filter_by(unique_id=unique_id).first_or_404()
    
    # Check if payment is already completed
    if payment_link.is_paid:
        return redirect(url_for('payment_success', unique_id=unique_id))
        
    # Check if link has expired (24 hours)
    if datetime.utcnow() - payment_link.created_at > timedelta(hours=24):
        flash('Ce lien de paiement a expiré. Veuillez en créer un nouveau.', 'error')
        return redirect(url_for('index'))
    
    return render_template('payment_page.html', 
                         product_name=payment_link.product_name,
                         price=payment_link.price,
                         delivery_cost=payment_link.delivery_cost,
                         delivery_method=payment_link.delivery_method,
                         total_amount=payment_link.total_amount,
                         unique_id=unique_id,
                         paypal_client_id=PAYPAL_CLIENT_ID)

@app.route('/create-paypal-order', methods=['POST'])
@csrf.exempt
def create_paypal_order():
    try:
        # Check if PayPal client is initialized
        if paypal_client is None:
            app.logger.error("PayPal client is not initialized")
            return jsonify({'error': 'Payment system not configured properly'}), 500
        
        if PAYPAL_ENVIRONMENT == 'sandbox':
            print("=== CREATE PAYPAL ORDER REQUEST ===")
        
        data = request.json
        unique_id = data.get('unique_id')
        
        payment_link = PaymentLink.query.filter_by(unique_id=unique_id).first_or_404()
        
        if PAYPAL_ENVIRONMENT == 'sandbox':
            print(f"Request data: {data}")
            print(f"Unique ID: {unique_id}")
            print(f"Payment link found: {payment_link.product_name}, Amount: {payment_link.total_amount}")
        
        # Create PayPal order
        request_paypal = OrdersCreateRequest()
        request_paypal.prefer('return=representation')
        
        order_data = {
            "intent": "CAPTURE",
            "purchase_units": [
                {
                    "reference_id": unique_id,
                    "amount": {
                        "currency_code": "EUR",
                        "value": f"{payment_link.total_amount:.2f}",
                        "breakdown": {
                            "item_total": {
                                "currency_code": "EUR",
                                "value": f"{payment_link.price:.2f}"
                            },
                            "shipping": {
                                "currency_code": "EUR",
                                "value": f"{payment_link.delivery_cost:.2f}"
                            }
                        }
                    },
                    "items": [
                        {
                            "name": payment_link.product_name,
                            "unit_amount": {
                                "currency_code": "EUR",
                                "value": f"{payment_link.price:.2f}"
                            },
                            "quantity": "1"
                        }
                    ]
                }
            ],
            "application_context": {
                "return_url": url_for('payment_success', unique_id=unique_id, _external=True),
                "cancel_url": url_for('payment_page', unique_id=unique_id, _external=True),
                "brand_name": "HijabiPay",
                "shipping_preference": "NO_SHIPPING",
                "user_action": "PAY_NOW"
            }
        }
        
        if PAYPAL_ENVIRONMENT == 'sandbox':
            print(f"Order data prepared: {order_data}")
            print("Sending request to PayPal...")
        
        request_paypal.request_body(order_data)
        response = paypal_client.client.execute(request_paypal)
        
        if PAYPAL_ENVIRONMENT == 'sandbox':
            print(f"PayPal Response Type: {type(response)}")
            print(f"PayPal Response Status Code: {response.status_code}")
        
        # Get the order ID from the response
        order_id = response.result.id if hasattr(response.result, 'id') else response.result.get('id')
        order_status = response.result.status if hasattr(response.result, 'status') else response.result.get('status', 'CREATED')
        
        if PAYPAL_ENVIRONMENT == 'sandbox':
            print(f"Order ID: {order_id}")
            print(f"Order Status: {order_status}")
        
        result = {
            'orderID': order_id,
            'status': order_status
        }
        
        if PAYPAL_ENVIRONMENT == 'sandbox':
            print(f"Returning JSON: {result}")
        
        return jsonify(result)
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        
        # Log detailed error for debugging (even in live mode temporarily)
        app.logger.error(f'Error creating PayPal order: {str(e)}')
        app.logger.error(f'Full traceback: {error_details}')
        
        # Check if it's a PayPal API error with details
        error_message = str(e)
        if hasattr(e, 'message'):
            error_message = e.message
        if hasattr(e, 'response'):
            error_message += f" | Response: {e.response}"
        
        if PAYPAL_ENVIRONMENT == 'sandbox':
            print(f"ERROR in create_paypal_order: {error_message}")
            traceback.print_exc()
        
        # Return more detailed error temporarily for debugging
        return jsonify({
            'error': 'Failed to create payment order',
            'details': error_message if PAYPAL_ENVIRONMENT == 'sandbox' else 'Check server logs for details'
        }), 500

@app.route('/capture-paypal-order', methods=['POST'])
@csrf.exempt
def capture_paypal_order():
    try:
        data = request.json
        order_id = data.get('orderID')
        unique_id = data.get('unique_id')
        
        if PAYPAL_ENVIRONMENT == 'sandbox':
            print(f"=== CAPTURING PAYPAL ORDER ===")
            print(f"Order ID: {order_id}, Unique ID: {unique_id}")
        
        payment_link = PaymentLink.query.filter_by(unique_id=unique_id).first_or_404()
        
        # Capture the PayPal order
        request_paypal = OrdersCaptureRequest(order_id)
        response = paypal_client.client.execute(request_paypal)
        
        if response.result.status == 'COMPLETED':
            # Update payment status in database
            payment_link.is_paid = True
            payment_link.payment_id = order_id
            payment_link.paid_at = datetime.utcnow()
            db.session.commit()
            
            return jsonify({
                'status': 'success',
                'message': 'Payment completed successfully',
                'redirect': url_for('payment_success', unique_id=unique_id)
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Payment not completed'
            }), 400
            
    except Exception as e:
        if PAYPAL_ENVIRONMENT == 'sandbox':
            print(f"ERROR in capture_paypal_order: {str(e)}")
            import traceback
            traceback.print_exc()
        app.logger.error(f'Error capturing PayPal order: {str(e)}')
        return jsonify({'status': 'error', 'message': 'Failed to process payment'}), 500

@app.route('/payment/success/<unique_id>')
def payment_success(unique_id):
    payment_link = PaymentLink.query.filter_by(unique_id=unique_id).first_or_404()
    return render_template('payment_success.html', payment_link=payment_link)

@app.route('/payment_link/edit/<unique_id>', methods=['GET', 'POST'])
def edit_payment_link(unique_id):
    payment_link = PaymentLink.query.filter_by(unique_id=unique_id).first_or_404()
    
    if request.method == 'POST':
        payment_link.product_name = request.form.get('product_name')
        payment_link.price = float(request.form.get('price'))
        payment_link.client_name = request.form.get('client_name')
        payment_link.delivery_method = request.form.get('delivery_method')
        
        db.session.commit()
        flash('Lien de paiement mis à jour avec succès!', 'success')
        return redirect(url_for('index'))
        
    return render_template('edit_link.html', link=payment_link)

@app.route('/payment_link/delete/<unique_id>', methods=['POST'])
def delete_payment_link(unique_id):
    payment_link = PaymentLink.query.filter_by(unique_id=unique_id).first_or_404()
    db.session.delete(payment_link)
    db.session.commit()
    flash('Lien de paiement supprimé avec succès!', 'success')
    return redirect(url_for('index'))

# API endpoint to check payment status
@app.route('/api/payment/status/<unique_id>')
def payment_status(unique_id):
    payment_link = PaymentLink.query.filter_by(unique_id=unique_id).first_or_404()
    return jsonify({
        'status': 'success' if payment_link.is_paid else 'pending',
        'payment_id': payment_link.payment_id,
        'product_name': payment_link.product_name,
        'amount': payment_link.price,
        'delivery_method': payment_link.delivery_method
    })

# Create database tables
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
