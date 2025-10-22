# ⚡ Quick Start - Deploy to PythonAnywhere in 10 Minutes

## 🎯 Step-by-Step (Copy & Paste)

### 1️⃣ Sign Up
- Go to: **https://www.pythonanywhere.com**
- Click **"Pricing & signup"**
- Choose **"Create a Beginner account"** (FREE)
- Complete registration

---

### 2️⃣ Open Bash Console
- Once logged in, click **"Consoles"** tab
- Click **"Bash"**

---

### 3️⃣ Clone & Setup (Copy/Paste This Block)

```bash
# Clone repository
git clone https://github.com/aminoz12/hijabipay.git
cd hijabipay

# Create virtual environment
python3.10 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create instance directory
mkdir -p instance
```

---

### 4️⃣ Create Environment File

```bash
# Create .env file
cat > .env << 'EOF'
SECRET_KEY=change-this-to-a-random-secret-key-123456789
DATABASE_URL=sqlite:///instance/payments.db
PAYPAL_CLIENT_ID=your-paypal-sandbox-client-id
PAYPAL_SECRET=your-paypal-sandbox-secret
PAYPAL_ENVIRONMENT=sandbox
EOF
```

**⚠️ Important:** Edit the `.env` file with your actual PayPal credentials:
```bash
nano .env
```
- Replace `your-paypal-sandbox-client-id` with your actual Client ID
- Replace `your-paypal-sandbox-secret` with your actual Secret
- Press `Ctrl+X`, then `Y`, then `Enter` to save

---

### 5️⃣ Initialize Database

```bash
python << 'EOF'
from app import app, db
with app.app_context():
    db.create_all()
    print("✅ Database created successfully!")
EOF
```

---

### 6️⃣ Configure Web App

1. Click **"Web"** tab (top menu)
2. Click **"Add a new web app"**
3. Click **"Next"** (accept the domain name)
4. Choose **"Manual configuration"**
5. Select **"Python 3.10"**
6. Click **"Next"**

---

### 7️⃣ Configure Settings

On the Web tab, update these sections:

#### A. Code Section
**Source code:** 
```
/home/YOUR_USERNAME/hijabipay
```
(Replace `YOUR_USERNAME` with your actual username - shown at top right)

#### B. Virtualenv Section
**Virtualenv:**
```
/home/YOUR_USERNAME/hijabipay/venv
```

#### C. WSGI Configuration
1. Click the **WSGI configuration file** link (e.g., `/var/www/YOUR_USERNAME_pythonanywhere_com_wsgi.py`)
2. **DELETE ALL** the existing code
3. **Paste this code:**

```python
import sys
import os

# IMPORTANT: Replace YOUR_USERNAME with your actual PythonAnywhere username!
project_home = '/home/YOUR_USERNAME/hijabipay'

if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Load environment variables
from dotenv import load_dotenv
load_dotenv(os.path.join(project_home, '.env'))

# Import Flask app
from app import app as application
```

4. **Replace `YOUR_USERNAME`** with your actual username (appears in 3 places)
5. Click **"Save"** (top right)

#### D. Static Files
Click **"+ Add a new static files mapping"**:
- **URL:** `/static/`
- **Directory:** `/home/YOUR_USERNAME/hijabipay/static/`

---

### 8️⃣ Reload & Launch! 🚀

1. Scroll to top of **Web** tab
2. Click the big green **"Reload"** button
3. Wait 5-10 seconds
4. Click your URL: **`https://YOUR_USERNAME.pythonanywhere.com`**

---

## ✅ Success Checklist

- [ ] Can access homepage
- [ ] Can create a payment link
- [ ] Can view payment page
- [ ] PayPal buttons load correctly

---

## 🐛 Troubleshooting

### Error 500 / Can't see the site?

**Check Error Log:**
1. Go to **Web** tab
2. Scroll to **"Log files"**
3. Click **"Error log"**
4. Look for the latest error

**Common fixes:**

```bash
# Go back to Bash console and run:
cd ~/hijabipay
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt

# Recreate database
python -c "from app import app, db; app.app_context().push(); db.create_all()"
```

Then **Reload** your web app.

---

## 🔄 Update Your App Later

When you push changes to GitHub:

```bash
cd ~/hijabipay
git pull origin main
source venv/bin/activate
pip install -r requirements.txt  # if needed
```

Then **Reload** the web app from the Web tab.

---

## 📞 Need Help?

- **PythonAnywhere Forums:** https://www.pythonanywhere.com/forums/
- **PythonAnywhere Help:** https://help.pythonanywhere.com/
- **Check Error Logs:** Web tab → Log files → Error log

---

## 🎉 That's It!

Your HijabiPay app is now live 24/7 at:
**`https://YOUR_USERNAME.pythonanywhere.com`**

No sleep, no downtime! 🚀

