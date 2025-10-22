# Installation Guide for Windows - HijabiPay

## Prerequisites Installation

You need to install Python and Node.js before running this application.

---

## Step 1: Install Python

### Download Python:

1. Go to: **https://www.python.org/downloads/**
2. Click on "Download Python 3.12.x" (or latest version)
3. **IMPORTANT:** During installation:
   - ✅ **Check the box "Add Python to PATH"** (Very Important!)
   - Click "Install Now"

### Verify Python Installation:

After installation, open a **NEW** PowerShell window and run:

```powershell
python --version
```

You should see something like: `Python 3.12.0`

Also verify pip:

```powershell
pip --version
```

You should see: `pip 23.x.x from ...`

---

## Step 2: Install Node.js

### Download Node.js:

1. Go to: **https://nodejs.org/**
2. Download the **LTS version** (Long Term Support)
3. Run the installer
4. Accept all defaults (it will automatically add to PATH)

### Verify Node.js Installation:

After installation, open a **NEW** PowerShell window and run:

```powershell
node --version
```

You should see something like: `v20.x.x`

Also verify npm:

```powershell
npm --version
```

You should see: `10.x.x`

---

## Step 3: Set Up HijabiPay Application

### 3.1 Navigate to the project folder:

```powershell
cd C:\Users\hp\Downloads\hijabiPay\hijabiPay-master
```

### 3.2 Create a virtual environment:

```powershell
python -m venv venv
```

### 3.3 Activate the virtual environment:

```powershell
.\venv\Scripts\activate
```

You should see `(venv)` appear at the beginning of your prompt.

### 3.4 Install Python dependencies:

```powershell
pip install -r requirements.txt
```

This will install Flask, SQLAlchemy, PayPal SDK, and other dependencies.

### 3.5 Install Node.js dependencies:

```powershell
npm install
```

This will install webpack and build tools.

---

## Step 4: Configure Environment Variables

### 4.1 Copy the example environment file:

```powershell
copy env.example .env
```

### 4.2 Edit the .env file:

Open the `.env` file in a text editor (Notepad, VS Code, etc.) and configure:

```env
# Flask Configuration
SECRET_KEY=your-secret-random-key-here-generate-something-long

# PayPal Configuration (REQUIRED)
PAYPAL_CLIENT_ID=your-paypal-client-id-here
PAYPAL_SECRET=your-paypal-secret-here
PAYPAL_ENVIRONMENT=sandbox

# Database
DATABASE_URL=sqlite:///payments.db
```

### 4.3 Get PayPal Credentials:

1. Go to: **https://developer.paypal.com/**
2. Log in or create a developer account (it's free)
3. Go to **Dashboard** → **My Apps & Credentials**
4. Under "Sandbox", click **"Create App"**
5. Give it a name (e.g., "HijabiPay")
6. Copy the **Client ID** and **Secret** to your `.env` file

---

## Step 5: Initialize Database

```powershell
python update_db.py
```

This creates the SQLite database with all necessary tables.

---

## Step 6: Run the Application

```powershell
python app.py
```

You should see:

```
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
```

Open your web browser and go to: **http://localhost:5000**

---

## Troubleshooting

### Problem: "python is not recognized"
**Solution:** You need to install Python and make sure "Add to PATH" is checked during installation.

### Problem: "pip is not recognized"
**Solution:** Same as above - reinstall Python with "Add to PATH" checked.

### Problem: "npm is not recognized"
**Solution:** Install Node.js from https://nodejs.org/

### Problem: "cannot activate venv"
**Solution:** Try this command instead:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```
Then try activating again:
```powershell
.\venv\Scripts\activate
```

### Problem: PayPal credentials error
**Solution:** Make sure you've:
1. Created a PayPal developer account
2. Created an app in the sandbox
3. Copied the correct Client ID and Secret to `.env`
4. Set `PAYPAL_ENVIRONMENT=sandbox` in `.env`

### Problem: Database errors
**Solution:** Delete the database and recreate:
```powershell
Remove-Item instance\payments.db -ErrorAction SilentlyContinue
python update_db.py
```

---

## Quick Command Reference

### Start the application (after initial setup):

```powershell
# Navigate to project
cd C:\Users\hp\Downloads\hijabiPay\hijabiPay-master

# Activate virtual environment
.\venv\Scripts\activate

# Run the app
python app.py
```

### Stop the application:
Press `Ctrl + C` in the PowerShell window

### Deactivate virtual environment:
```powershell
deactivate
```

---

## System Requirements

- **Windows 10 or later**
- **Python 3.8+** (recommended: 3.12)
- **Node.js 16+** (recommended: 20 LTS)
- **4GB RAM minimum**
- **Internet connection** (for PayPal integration)

---

## Next Steps After Installation

1. ✅ Create payment links
2. ✅ Test payments in PayPal sandbox
3. ✅ When ready for production:
   - Get live PayPal credentials
   - Change `.env` to `PAYPAL_ENVIRONMENT=live`
   - Deploy to a production server

---

## Support

If you encounter any issues:
1. Check this guide carefully
2. Make sure Python and Node.js are properly installed
3. Verify your PayPal credentials are correct
4. Check the console for error messages

---

## Important Notes

- **Always activate the virtual environment** before running the app
- **Never commit your `.env` file** to version control (it's already in .gitignore)
- **Use sandbox mode** for testing, never use live credentials for testing
- **Keep your SECRET_KEY secret** - generate a new one for production

---

Good luck! 🚀

