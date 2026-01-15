import os
import time
import platform
import logging
import requests
import psutil
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# ================= CONFIG =================
BOT_TOKEN = os.getenv("BOT_TOKEN")
GH_TOKEN = os.getenv("GH_TOKEN")

# CHANGE THESE TWO ONLY
GITHUB_OWNER ="bykoviaz454-png"
GITHUB_REPO = "VPS"
WORKFLOW_FILE = "bot.yml"
# =========================================

START_TIME = time.time()
LOG_FILE = "bot.log"

# ---------------- LOGGING ----------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

HEADERS = {
    "Authorization": f"token {GH_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

# ---------------- BASIC ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Public VPS Dashboard Bot\n\n"
        "Use /dashboard to see server panel\n"
        "Use /help for commands"
    )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🛠 COMMANDS\n\n"
        "/dashboard\n/ping\n/uptime\n/logs\n\n"
        "/cpu /ram /disk\n/os /python\n\n"
        "/status /run /lastbuild\n\n"
        "/restart /stop"
    )

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🏓 Pong! Bot is alive")

async def uptime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"⏱ Uptime: {int(time.time() - START_TIME)} sec"
    )

# ---------------- SYSTEM ----------------
async def cpu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"🧠 CPU Usage: {psutil.cpu_percent(interval=1)}%\n"
        f"Cores: {psutil.cpu_count()}"
    )

async def ram(update: Update, context: ContextTypes.DEFAULT_TYPE):
    m = psutil.virtual_memory()
    await update.message.reply_text(
        f"💾 RAM\n"
        f"Total: {round(m.total/1024**3,2)} GB\n"
        f"Used: {round(m.used/1024**3,2)} GB\n"
        f"Free: {round(m.available/1024**3,2)} GB\n"
        f"Usage: {m.percent}%"
    )

async def disk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    d = psutil.disk_usage("/")
    await update.message.reply_text(
        f"📀 Disk\n"
        f"Total: {round(d.total/1024**3,2)} GB\n"
        f"Used: {round(d.used/1024**3,2)} GB\n"
        f"Free: {round(d.free/1024**3,2)} GB\n"
        f"Usage: {d.percent}%"
    )

async def osinfo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"🖥 OS: {platform.system()} {platform.release()}"
    )

async def python_ver(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"🐍 Python: {platform.python_version()}"
    )

# ---------------- DASHBOARD ----------------
async def dashboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cpu = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage("/")

    try:
        url = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/actions/runs"
        r = requests.get(url, headers=HEADERS).json()
        run = r["workflow_runs"][0]
        wf_status = run["status"]
        wf_result = run["conclusion"]
    except:
        wf_status = "unknown"
        wf_result = "unknown"

    msg = f"""
📊 *PUBLIC VPS DASHBOARD*

🟢 Bot: Online
⏱ Uptime: {int(time.time() - START_TIME)} sec

🧠 CPU: {cpu}%
💾 RAM: {mem.percent}%
📀 Disk: {disk.percent}%

⚙️ System
• OS: {platform.system()} {platform.release()}
• Python: {platform.python_version()}

🔄 GitHub Workflow
• Status: {wf_status}
• Result: {wf_result}
"""
    await update.message.reply_text(msg, parse_mode="Markdown")

# ---------------- LOGS ----------------
async def logs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not os.path.exists(LOG_FILE):
        await update.message.reply_text("📭 No logs yet")
        return
    data = open(LOG_FILE).read().strip()
    await update.message.reply_text(
        "📜 Logs:\n\n" + data[-3500:]
    )

# ---------------- GITHUB ----------------
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/actions/runs"
    r = requests.get(url, headers=HEADERS).json()
    run = r["workflow_runs"][0]
    await update.message.reply_text(
        f"📊 Status: {run['status']}\nResult: {run['conclusion']}"
    )

async def runflow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/actions/workflows/{WORKFLOW_FILE}/dispatches"
    r = requests.post(url, headers=HEADERS, json={"ref": "main"})
    await update.message.reply_text(
        "▶️ Workflow started" if r.status_code == 204 else "❌ Failed"
    )

async def lastbuild(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/actions/runs"
    r = requests.get(url, headers=HEADERS).json()
    run = r["workflow_runs"][0]
    await update.message.reply_text(
        f"🧾 Last Build\n{run['status']} | {run['conclusion']}"
    )

# ---------------- CONTROL ----------------
async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔄 Restarting bot...")
    os._exit(0)

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🛑 Bot stopped (cron will restart)")
    exit(0)

# ---------------- MAIN ----------------
app = ApplicationBuilder().token(BOT_TOKEN).build()

handlers = {
    "start": start,
    "help": help_cmd,
    "dashboard": dashboard,
    "ping": ping,
    "uptime": uptime,
    "cpu": cpu,
    "ram": ram,
    "disk": disk,
    "os": osinfo,
    "python": python_ver,
    "logs": logs,
    "status": status,
    "run": runflow,
    "lastbuild": lastbuild,
    "restart": restart,
    "stop": stop,
}

for c, f in handlers.items():
    app.add_handler(CommandHandler(c, f))

logger.info("🤖 VPS Dashboard Bot Started")
app.run_polling()