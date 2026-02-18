# 🪄 Account Gen Bot

A Discord bot for generating accounts with a premium system, cooldowns, and key-based access.

> Dev by **g1p9**

---

## 📦 Features

- Generate accounts via `/gen` or `+gen`
- Stock display with `+stock`
- Premium system with key redemption
- Cooldown system (different for premium users)
- Automatic premium role removal on expiry
- Persistent redeem button/modal

---

## 🚀 Setup

**1. Clone the repo**
```bash
git clone https://github.com/yourname/account-gen-bot.git
cd account-gen-bot
```

**2. Run the setup script**
```bash
setup.bat
```

**3. Fill in your `settings.json`**
```json
{
  "token": "YOUR_BOT_TOKEN",
  "restock_channel": "CHANNEL_ID",
  "couleur": "0x5865F2",
  "owner_id": "YOUR_USER_ID",
  "cooldown": "600",
  "premium": {
    "cooldown": "120",
    "role_id": "ROLE_ID",
    "sys_enabled": true
  }
}
```

**4. Fill in your `stock.json`**
```json
{
  "roblox": ["user1:pass1", "user2:pass2"],
  "netflix": []
}
```

**5. Start the bot**
```bash
run.bat
```

---

## 🤖 Commands

| Command | Description | Access |
|---|---|---|
| `+stock` | Show available stock | Everyone |
| `/gen [type]` | Generate an account (slash) | Everyone |
| `+gen [type]` | Generate an account (prefix) | Everyone |
| `+createkey [days]` | Create a premium key (-1 = permanent) | Owner only |
| `+send_redeem` | Send the premium redeem panel | Owner only |
| `/redeem` | Redeem a premium key | Everyone |

---

## ⭐ Premium System

- Use `+createkey 30` to create a 30-day key
- Use `+createkey -1` for a permanent key
- Users redeem via the panel sent with `+send_redeem`
- Premium users get a shorter cooldown between generations
- Role is automatically removed when the key expires
- Set `sys_enabled: false` in `settings.json` to disable the system entirely

---

## 📁 File Structure

```
account-gen-bot/
├── bot.py
├── settings.json
├── stock.json
├── keys.json        # auto-generated
├── cooldowns.json   # auto-generated
├── banner.txt
├── setup.bat
└── run.bat
```

---

## ⚙️ Requirements

- Python 3.10+
- discord.py

```bash
pip install discord.py
```
