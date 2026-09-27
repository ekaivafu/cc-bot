# CC Bot (Telegram Bot)

**Developer Telegram:** [@tgekaiva](https://t.me/tgekaiva)

A Telegram Bot for card verification and processing with Braintree sandbox flow, prepared for deployment on Render.

## Features

- Telegram commands:
  - `/start` - Start interaction with the bot
  - `/help` - Show available commands and format
  - `/cc <ccnum>|<month>|<year>|<cvv>` - Process a card
- Background health check server on port `$PORT` (compatible with Render Free Web Service)
- Environment variable configuration for secure token handling

---

## Deploying on Render (Free Tier)

Render's free tier supports **Web Services**. This bot includes a lightweight built-in HTTP server to respond to Render's port checks automatically.

### Step 1: Push code to GitHub
Make sure this repository is pushed to your GitHub account (e.g. `https://github.com/ekaivafu/cc-bot.git`).

### Step 2: Create a New Web Service on Render
1. Log in to [Render Dashboard](https://dashboard.render.com/).
2. Click **New +** > **Web Service**.
3. Connect your GitHub account and select your repository (`cc-bot`).
4. Configure the service settings:
   - **Name**: `cc-bot` (or any name you prefer)
   - **Language / Runtime**: `Python 3`
   - **Branch**: `main` (or `master`)
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python bot.py`
   - **Instance Type**: `Free`

### Step 3: Add Environment Variables
Scroll down to the **Environment Variables** section in Render and add:
- `BOT_TOKEN`: Your Telegram Bot token from [@BotFather](https://t.me/BotFather)

*(Optional)* You can also configure:
- `BT_MERCHANT_ID`
- `BT_PUBLIC_KEY`
- `BT_PRIVATE_KEY`

### Step 4: Deploy
Click **Create Web Service**. Render will install requirements and start your bot!

---

## Running Locally

1. **Clone the repository:**
   ```bash
   git clone https://github.com/ekaivafu/cc-bot.git
   cd cc-bot
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   # Windows:
   .\venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set your bot token and run:**
   ```bash
   # Windows (PowerShell):
   $env:BOT_TOKEN="YOUR_TELEGRAM_BOT_TOKEN"
   python bot.py

   # Linux/macOS:
   export BOT_TOKEN="YOUR_TELEGRAM_BOT_TOKEN"
   python bot.py
   ```
