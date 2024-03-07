from typing import List
from dotenv import load_dotenv
import os
import logging
from telegram import Update
from telegram.ext import (
    filters,
    MessageHandler,
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)
import docker
import subprocess
import io

# get token from environment
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
assert TOKEN is not None

# configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(name)s", level=logging.INFO
)

# state: running processes
running: List[str] = []

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    assert update.effective_chat is not None
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Hi there")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    assert update.effective_chat is not None
    assert update.message is not None
    assert update.message.text is not None
    to_send = update.message.text
    await context.bot.send_message(chat_id=update.effective_chat.id, text=to_send)


async def run(update: Update, context: ContextTypes.DEFAULT_TYPE):
    assert update.effective_chat is not None

    if context.args is None:
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text="Provide a notebook name."
        )
        return

    notebook = context.args[0]

    #TODO: check if the cid file already exists
    # this means that the notebook is already running:
    # inform the user about this, send a message, don't create a new instance
    # Later, find out how to handle multiple instances of the same image
    # (multiple instances of a PyTorch notebook)

    # get link with token

    # result = subprocess.run(docker.docker_command, capture_output=True, text=True)
    # output = result.stdout

    print(f'Running {docker.docker_command}')
    docker_process = subprocess.Popen(
        docker.docker_command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    output = 'empty'
    for line in io.TextIOWrapper(docker_process.stderr, encoding="utf-8"):
        output = line
        if 'http://127.0.0.1:8888' in line:
            break
    print(output)

    # while True:
    #     output = docker_process.stdout.readline().decode()
    #     print(output)
    #     if 'copy and paste' in output:
    #         break
        
    # get DOCKER PID
    with open(docker.CIDFILE, 'r') as cidfile:
        pid = cidfile.read()
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f'PID: {pid}')

    response = f"Running notebook: {notebook}"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=output)


async def kill(update: Update, context: ContextTypes.DEFAULT_TYPE):
    assert update.effective_chat is not None
    assert context.args is not None
    notebook = context.args[0]
    response = f"Killing notebook: {notebook}"
    # docker kill DOCKER_PID
    # remove CIDFILE
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response)


async def ps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    assert update.effective_chat is not None
    response = f"Currently running: {running}"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response)

def main() -> None:
    """Run the bot."""
    application = ApplicationBuilder().token(TOKEN).build()

    start_handler = CommandHandler("start", start)
    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
    run_handler = CommandHandler("run", run)
    kill_handler = CommandHandler("kill", kill)
    ps_handler = CommandHandler("ps", ps)

    application.add_handler(start_handler)
    application.add_handler(echo_handler)
    application.add_handler(run_handler)
    application.add_handler(kill_handler)
    application.add_handler(ps_handler)

    application.run_polling()


if __name__ == "__main__":
    main()
