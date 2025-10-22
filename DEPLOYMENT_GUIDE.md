# 🚀 PythonAnywhere Deployment Guide for HijabiPay

## Prerequisites
- GitHub account with your code pushed
- PythonAnywhere account (free tier)

---

## Step 1: Create PythonAnywhere Account

1. Go to **https://www.pythonanywhere.com**
2. Click **"Start running Python online in less than a minute!"**
3. Choose the **Beginner (Free)** account
4. Sign up with your email

---

## Step 2: Clone Your Repository

1. Once logged in, go to **"Consoles"** tab
2. Click **"Bash"** to open a new console
3. Run these commands:

```bash
# Clone your repository
git clone https://github.com/aminoz12/hijabipay.git

# Navigate to the project
cd hijabipay

# Create virtual environment
python3.10 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## Step 3: Set Up Environment Variables

1. In the same Bash console:

```bash
# Create .env file
nano .env
```

2. Add your environment variables:

```env
SECRET_KEY=your-secret-key-here-change-this-to-something-random
DATABASE_URL=sqlite:///instance/payments.db
PAYPAL_CLIENT_ID=your-paypal-client-id
PAYPAL_SECRET=your-paypal-secret
PAYPAL_ENVIRONMENT=sandbox
```

3. Press `Ctrl+X`, then `Y`, then `Enter` to save

---

## Step 4: Initialize Database

```bash
# Make sure you're in the project directory and venv is activated
cd ~/hijabipay
source venv/bin/activate

# Create instance directory
mkdir -p instance

# Initialize the database
python << EOF
from app import app, db
with app.app_context():
    db.create_all()
    print("Database created successfully!")
EOF
```

---

## Step 5: Configure Web App

1. Go to **"Web"** tab in PythonAnywhere
2. Click **"Add a new web app"**
3. Choose **"Manual configuration"** (NOT Flask)
4. Select **Python 3.10**

### Configure the following sections:

#### A. Source Code
- **Source code:** `/home/YOUR_USERNAME/hijabipay`

#### B. WSGI Configuration File
1. Click on the WSGI configuration file link
2. **Delete all the content**
3. Replace with:

```python
import sys
import os

# Add your project directory to the sys.path
project_home = '/home/YOUR_USERNAME/hijabipay'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Load environment variables
from dotenv import load_dotenv
load_dotenv(os.path.join(project_home, '.env'))

# Import Flask app
from app import app as application
```

**Important:** Replace `YOUR_USERNAME` with your actual PythonAnywhere username!

#### C. Virtualenv
- **Virtualenv:** `/home/YOUR_USERNAME/hijabipay/venv`

#### D. Static Files
Add these mappings:

| URL | Directory |
|-----|-----------|
| `/static/` | `/home/YOUR_USERNAME/hijabipay/static/` |

---

## Step 6: Reload Your Web App

1. Scroll to the top of the **Web** tab
2. Click the big green **"Reload YOUR_USERNAME.pythonanywhere.com"** button
3. Wait a few seconds for it to reload

---

## Step 7: Test Your Application

1. Click on your URL: **https://YOUR_USERNAME.pythonanywhere.com**
2. You should see your HijabiPay homepage!
3. Test creating a payment link
4. Test the payment flow

---

## 🔧 Troubleshooting

### View Error Logs
1. Go to **Web** tab
2. Scroll down to **"Log files"**
3. Click on **Error log** to see any errors

### Common Issues:

**1. "ModuleNotFoundError"**
```bash
cd ~/hijabipay
source venv/bin/activate
pip install -r requirements.txt
```

**2. "Database error"**
```bash
cd ~/hijabipay
source venv/bin/activate
python -c "from app import app, db; app.app_context().push(); db.create_all()"
```

**3. "Static files not loading"**
- Check Static Files mapping in Web tab
- Make sure paths are correct

**4. "500 Internal Server Error"**
- Check error log in Web tab
- Make sure .env file exists with correct values
- Verify WSGI file has correct username

---

## 🔄 Updating Your App

When you make changes to your code:

```bash
cd ~/hijabipay
git pull origin main
source venv/bin/activate
pip install -r requirements.txt  # if requirements changed
```

Then **Reload** your web app from the Web tab.

---

## 📝 Important Notes

1. **Free tier limitations:**
   - Your app URL will be: `YOUR_USERNAME.pythonanywhere.com`
   - Limited CPU time per day
   - No custom domain (upgrade needed)
   - Access restricted to HTTP (HTTPS available on paid plans for custom domains)

2. **Database:**
   - SQLite is used (file-based)
   - Located at: `/home/YOUR_USERNAME/hijabipay/instance/payments.db`
   - For production, consider upgrading to MySQL

3. **PayPal Configuration:**
   - Make sure to use your PayPal sandbox credentials for testing
   - Switch to live credentials when ready for production

4. **Security:**
   - Change the SECRET_KEY to a random string
   - Never commit .env to GitHub
   - Keep your PayPal credentials secure

---

## 🎉 Success!

Your HijabiPay application should now be live and accessible 24/7 at:
**https://YOUR_USERNAME.pythonanywhere.com**

For support or questions, check the PythonAnywhere forums or documentation.

---

## 🚀 Next Steps

1. Test all payment flows thoroughly
2. Set up proper logging
3. Monitor your daily CPU usage
4. Consider upgrading to a paid plan for:
   - Custom domain
   - More CPU time
   - MySQL database
   - SSH access

