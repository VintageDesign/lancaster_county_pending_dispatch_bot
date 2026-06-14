# Lancaster County Pending Dispatch Bot (Premonition)

Monitors the [LCWC Live Incident List](https://www.lcwc911.us/live-incident-list) and sends a Telegram message when a new **Active Fire Incident** matches configured keywords.

## Requirements

```
pip install requests
```

## Configuration

Two environment variables are required before running:

| Variable | Description |
|---|---|
| `TELEGRAM_BOT_TOKEN` | Bot token from [@BotFather](https://t.me/BotFather) |
| `TELEGRAM_CHAT_ID` | ID of the chat/group to post alerts to |

### Setting environment variables

**Linux / macOS (session)**
```bash
export TELEGRAM_BOT_TOKEN="your-token-here"
export TELEGRAM_CHAT_ID="your-chat-id-here"
```

**Linux / macOS (permanent — add to `~/.bashrc` or `~/.zshrc`)**
```bash
echo 'export TELEGRAM_BOT_TOKEN="your-token-here"' >> ~/.bashrc
echo 'export TELEGRAM_CHAT_ID="your-chat-id-here"' >> ~/.bashrc
source ~/.bashrc
```

**`.env` file (with a tool like `python-dotenv` or `direnv`)**
```
TELEGRAM_BOT_TOKEN=your-token-here
TELEGRAM_CHAT_ID=your-chat-id-here
```
Then: `direnv allow` or load with `source .env` before running.

**systemd service**

Use the provided `premonition.env.example` as a template:
```bash
cp premonition.env.example ~/.config/premonition.env
chmod 600 ~/.config/premonition.env
$EDITOR ~/.config/premonition.env
```

### Getting your Chat ID

1. Add your bot to the target group.
2. Send a message in the group.
3. Fetch: `https://api.telegram.org/bot<TOKEN>/getUpdates`
4. Look for `"chat":{"id": ...}` in the response — that number is your `TELEGRAM_CHAT_ID`. Groups will have a negative ID (e.g. `-1001234567890`).

## Running

```bash
python3 premonition.py
```

The script polls the feed every 30 seconds and prints/sends alerts for any new incident matching the keywords in `KEYWORDS`.

## Running as a systemd service (auto-start on boot)

```bash
# 1. Set up credentials
cp premonition.env.example ~/.config/premonition.env
chmod 600 ~/.config/premonition.env
$EDITOR ~/.config/premonition.env

# 2. Install the service
mkdir -p ~/.config/systemd/user
cp premonition.service ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now premonition.service

# 3. Check status / logs
systemctl --user status premonition.service
journalctl --user -u premonition.service -f
```

If the machine boots without an active login session, also run:
```bash
loginctl enable-linger $USER
```

## Customization

- **Keywords:** Edit the `KEYWORDS` list in `premonition.py` to match your jurisdiction, station, or unit. Matched against incident type + location (case-insensitive).
- **Poll interval:** Adjust `POLL_INTERVAL` (seconds). The page refreshes every 2 minutes; 30s default gives you prompt alerts without hammering the server.
- **Scope:** Only the **Active Fire Incidents** table is monitored. Medical and traffic tables are ignored.
