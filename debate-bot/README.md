# Telegram Debate Bot

A personal Telegram bot that debates you on your own blog posts. It scrapes a random post from `sreekarscribbles.com`, then acts as a sharp intellectual opponent — challenging your thesis, using your own words against you, and asking pointed questions until you either defend your ideas or concede ground.

Runs on a Raspberry Pi Zero 2W as a systemd service.

---

## Prerequisites

### 1. Check Python version on your RPi

```bash
python3 --version
# Should be 3.11 or higher
```

If Python 3.11+ isn't available:
```bash
sudo apt update && sudo apt install -y python3.11 python3.11-venv python3-pip
```

### 2. Install build tools (needed for lxml on ARM)

```bash
sudo apt install -y gcc libxml2-dev libxslt1-dev
```

---

## Setup

### 3. Clone the repo

```bash
cd /home/pi
git clone <your-repo-url> debate-bot
cd debate-bot
```

Or copy files manually if not using git.

### 4. Create a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 5. Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

> On a Pi Zero 2W, `lxml` compilation may take a few minutes. Be patient.

---

## API Keys & Config

### 6. Create a Telegram bot via @BotFather

1. Open Telegram and search for **@BotFather**
2. Send `/newbot`
3. Choose a name (e.g. "Sreekar's Debate Bot") and a username (e.g. `sreekar_debate_bot`)
4. BotFather will give you a token like `7123456789:AAHxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
5. Keep this — it's your `TELEGRAM_BOT_TOKEN`

### 7. Get a free Gemini API key

1. Go to [aistudio.google.com](https://aistudio.google.com)
2. Sign in with your Google account
3. Click **Get API key** → **Create API key**
4. Copy the key — this is your `GEMINI_API_KEY`

> **Important:** Create the key from within AI Studio (not Google Cloud Console) and choose **"Create new project"** — this ensures the free tier is enabled. The bot uses `gemini-2.5-flash` (5 requests/min free tier), which is plenty for personal use.

### 8. Find your Telegram chat ID

1. Open Telegram and search for **@userinfobot**
2. Send `/start`
3. It will reply with your User ID — that's your `YOUR_CHAT_ID`

### 9. Set up the `.env` file

```bash
cp .env.example .env
nano .env
```

Fill in:
```
TELEGRAM_BOT_TOKEN=7123456789:AAHxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
GEMINI_API_KEY=AIzaSyXxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
YOUR_CHAT_ID=123456789
```

---

## Running Locally (Test First)

```bash
source venv/bin/activate
python bot.py
```

Open Telegram on your phone, find your bot, and:
- Send `/start` — should get a welcome message
- Send `/debate` — should pick a post and send Gemini's opening challenge
- Reply to continue the debate
- Send `/end` — should get a 2-line summary

If everything works, set up the systemd service.

---

## Running as a systemd Service (Runs on Boot)

### 10. Install the service

```bash
sudo cp debate-bot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable debate-bot
sudo systemctl start debate-bot
sudo systemctl status debate-bot   # should show "active (running)"
```

### Check logs

```bash
journalctl -u debate-bot -f
```

### Useful service commands

```bash
sudo systemctl stop debate-bot      # stop the bot
sudo systemctl restart debate-bot   # restart after config changes
sudo systemctl disable debate-bot   # stop it from starting on boot
```

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `ModuleNotFoundError` | Make sure you're using the venv Python: `/home/pi/debate-bot/venv/bin/python` |
| RSS fetch fails | Check Ghost is running: `curl http://localhost:2368/rss` |
| Gemini returns empty | Check your `GEMINI_API_KEY` in `.env` and that the key has API access |
| Bot doesn't respond | Verify `YOUR_CHAT_ID` matches your actual Telegram user ID |
| lxml build fails | `sudo apt install -y gcc libxml2-dev libxslt1-dev` then reinstall |
| Service won't start | Check `journalctl -u debate-bot -n 50` for the error |

---

## Project Structure

```
debate-bot/
├── bot.py              # Telegram bot — command and message handlers
├── scraper.py          # RSS fetch + Ghost HTML scraper
├── debater.py          # Gemini API — debate logic and history management
├── requirements.txt    # Pinned Python dependencies
├── .env.example        # Template for secrets
├── debate-bot.service  # systemd unit file
└── README.md
```

---

## How It Works

1. `/debate` → `scraper.py` fetches your RSS feed (localhost first, public URL fallback), picks a random post, scrapes full content
2. `debater.py` sends the post to Gemini 1.5 Flash with a system prompt instructing it to act as an opponent
3. Gemini opens with a challenge targeting your post's main thesis
4. Each reply you send is appended to conversation history and sent back to Gemini for a contextual counter-argument
5. `/end` → Gemini summarises what was argued and the debate session is cleared
