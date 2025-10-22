# HijabiPay - Payment Gateway

A Flask-based payment gateway application that uses PayPal for processing payments. This application allows you to create payment links for products with delivery options.

## Features

- Create payment links with custom product names and prices
- Support for delivery costs and methods
- PayPal integration for secure payments
- 24-hour expiration for payment links
- Payment tracking and management
- Responsive design with Tailwind CSS

## Prerequisites

- Python 3.8 or higher
- Node.js and npm (for frontend build tools)
- PayPal Developer Account (for API credentials)

## Installation

### 1. Clone the repository

```bash
cd hijabiPay-master
```

### 2. Create a virtual environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 4. Install Node.js dependencies

```bash
npm install
```

### 5. Set up environment variables

Copy the `env.example` file to `.env` and fill in your configuration:

```bash
# Windows
copy env.example .env

# Linux/Mac
cp env.example .env
```

Edit the `.env` file and add your PayPal credentials:

```env
SECRET_KEY=your-secret-key-here
PAYPAL_CLIENT_ID=your-paypal-client-id
PAYPAL_SECRET=your-paypal-secret
PAYPAL_ENVIRONMENT=sandbox
```

**To get PayPal credentials:**
1. Go to https://developer.paypal.com/
2. Log in or create a developer account
3. Go to Dashboard > My Apps & Credentials
4. Create a new app or use an existing one
5. Copy the Client ID and Secret

### 6. Initialize the database

```bash
python update_db.py
```

Or use Flask-Migrate:

```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

## Running the Application

### Development Mode

```bash
# Run the Flask application
python app.py
```

The application will be available at `http://localhost:5000`

### Build Frontend Assets (Optional)

```bash
# Development mode with watch
npm run dev

# Production build
npm run build
```

## Usage

1. **Create a Payment Link**
   - Navigate to the home page
   - Click "Créer un lien de paiement"
   - Fill in product details (name, price, delivery method, etc.)
   - Submit the form
   - Copy the generated payment link

2. **Share the Link**
   - Send the payment link to your customer
   - They can complete the payment using PayPal

3. **Track Payments**
   - View all recent payment links on the home page
   - Check payment status (paid/unpaid)
   - Edit or delete payment links as needed

## Project Structure

```
hijabiPay-master/
├── app.py                  # Main Flask application
├── requirements.txt        # Python dependencies
├── package.json           # Node.js dependencies
├── webpack.config.js      # Webpack configuration
├── env.example            # Environment variables template
├── update_db.py           # Database initialization script
├── instance/
│   └── payments.db        # SQLite database
├── migrations/            # Flask-Migrate database migrations
├── static/
│   ├── css/              # Stylesheets
│   ├── images/           # Images and logos
│   └── js/               # JavaScript files
└── templates/            # HTML templates
    ├── base.html         # Base template
    ├── index.html        # Home page
    ├── create_link.html  # Create payment link form
    ├── payment_page.html # Payment processing page
    └── payment_success.html # Success confirmation
```

## Database Schema

### PaymentLink Model

- `id`: Primary key
- `product_name`: Name of the product
- `price`: Product price
- `delivery_cost`: Delivery cost
- `client_name`: Customer name
- `delivery_method`: Delivery method
- `unique_id`: Unique identifier for the payment link
- `created_at`: Creation timestamp
- `is_paid`: Payment status
- `payment_id`: PayPal transaction ID
- `paid_at`: Payment completion timestamp

## Security Features

- CSRF protection for all forms
- Secure PayPal integration
- Environment-based configuration
- 24-hour link expiration
- Server-side payment validation

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Flask secret key for sessions | Random generated |
| `DATABASE_URL` | Database connection URL | `sqlite:///payments.db` |
| `PAYPAL_CLIENT_ID` | PayPal API Client ID | Required |
| `PAYPAL_SECRET` | PayPal API Secret | Required |
| `PAYPAL_ENVIRONMENT` | PayPal environment (sandbox/live) | `sandbox` |

## Troubleshooting

### PayPal SDK Not Loading

- Check your PayPal Client ID is correct
- Ensure you have internet connection
- Check browser console for errors
- Try clearing browser cache

### Database Errors

- Run `python update_db.py` to recreate the database
- Check file permissions on the `instance/` directory

### CSRF Token Errors

- Ensure SECRET_KEY is set in .env
- Clear browser cookies
- Check that CSRF protection is enabled

## Production Deployment

### Important Changes for Production:

1. **Set environment to production:**
   ```env
   PAYPAL_ENVIRONMENT=live
   FLASK_DEBUG=False
   FLASK_ENV=production
   ```

2. **Use a production database:**
   ```env
   DATABASE_URL=postgresql://user:password@host:port/dbname
   ```

3. **Generate a strong SECRET_KEY:**
   ```python
   import secrets
   print(secrets.token_hex(32))
   ```

4. **Use a production WSGI server:**
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:8000 app:app
   ```

5. **Set up HTTPS** (required for PayPal live mode)

## Support

For issues or questions, contact support via WhatsApp at the number provided in the application.

## License

This project is proprietary software. All rights reserved.

## Version

1.0.0

