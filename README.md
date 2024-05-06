# remote-jupyter-bot
A Telegram bot that serves links to remote Jupyter notebook sessions

# Installation

You need:
* A UNIX machine (I use Debian)
* bash
* Python (at least 3.10, I use 3.12)
* Docker
* A Telegram bot token that you obtain from BotFather

# Setup

1. Clone the repo
```bash
git clone git@github.com:kotleta2007/remote-jupyter-bot.git
```
2. Create a virtual environment, install the dependencies
```bash
python -m virtualenv bot
source bot/bin/activate
pip install -r requirements.txt
```
3. Put your bot token in `.env`
```bash
echo TELEGRAM_TOKEN=YOUR_TOKEN_HERE > .env
```
4. Run the script
```bash
./jupyter-bot.sh
```

# Usage

The `/man` command lists all available commands.
