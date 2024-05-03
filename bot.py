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
import pathlib
import notebooks

# get token from environment
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
assert TOKEN is not None

# configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(name)s", level=logging.INFO
)

# Map(Name -> CID)
running = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    assert update.effective_chat is not None
    # create notebooks.csv for INIT command
    pathlib.Path(notebooks.CSV_FILEPATH).expanduser().touch()
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Hi there")


async def init(update: Update, context: ContextTypes.DEFAULT_TYPE):
    assert update.effective_chat is not None

    if len(context.args) != 2:
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text="Provide a notebook name and type."
        )
    
    alias, name = context.args[0], context.args[1]
    notebook_created = notebooks.put(alias, name)
    print(notebook_created)

    if notebook_created:
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text=f"{name} is now saved as {alias}."
        )
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text=f"{alias} is already taken! Try again."
        )

async def run(update: Update, context: ContextTypes.DEFAULT_TYPE):
    assert update.effective_chat is not None

    if context.args is None or len(context.args) == 0:
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text="Provide a notebook name."
        )
        return
    
    assert len(context.args) == 1
    notebook = context.args[0]

    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text=f'Starting notebook: {notebook}'
    )

    #TODO: check if the cid file already exists
    # this means that the notebook is already running:
    # inform the user about this, send a message, don't create a new instance
    # Later, find out how to handle multiple instances of the same image
    # (multiple instances of a PyTorch notebook)

    # print(f'Running {docker.docker_command}')
    docker_process = subprocess.Popen(
        ' '.join(docker.run(HOST_PORT=60000, notebook_name=notebook)),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True
    )

    # parse jupyter token
    output = ''
    for line in io.TextIOWrapper(docker_process.stderr, encoding="utf-8"):
        print(line)
        output = line
        if 'http://127.0.0.1:8888' in line:
            break
    output = docker.get_token(output)

    # get DOCKER PID
    with open(docker.CIDFILE, 'r') as cidfile:
        pid = cidfile.read()
        global running
        running[notebook] = pid
    # remove CIDFILE
    pathlib.Path.unlink(docker.CIDFILE)

    await context.bot.send_message(chat_id=update.effective_chat.id, text=f'Your token: {output}')


async def kill(update: Update, context: ContextTypes.DEFAULT_TYPE):
    assert update.effective_chat is not None
    assert context.args is not None
    assert len(context.args) == 1
    notebook = context.args[0]
    
    global running
    if notebook not in running.keys():
        await context.bot.send_message(
            chat_id=update.effective_chat.id, 
            text='No such notebook currently running.'
        )
        return
    
    # kill the docker container
    docker_process = subprocess.Popen(
        docker.docker_kill_command(running[notebook]),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    # remove the key-value pair from the dictionary
    del running[notebook]

    response = f"Killed notebook: {notebook}"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response)


async def ps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    assert update.effective_chat is not None
    response = f"Currently running: {running}"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response)

async def noop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    assert update.effective_chat is not None
    response = "Unrecognized command. Use /man to get list of commands."
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response)

async def man(update: Update, context: ContextTypes.DEFAULT_TYPE):
    assert update.effective_chat is not None
    response = "Commands:"
    response += "\n/man [COMMAND] -- describe a command OR list all commands"
    response += "\n/ls -- view available Jupyter notebooks"
    response += "\n/ps -- view currently running Jupyter notebooks"
    response += "\n/start -- create a local table of notebooks"
    response += "\n/init -- add a new notebook"
    response += "\n/kill -- kill a running instance of a notebook"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response)


def main() -> None:
    """Run the bot."""
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("run", run))
    application.add_handler(CommandHandler("kill", kill))
    application.add_handler(CommandHandler("ps", ps))
    application.add_handler(CommandHandler("init", init))
    application.add_handler(CommandHandler("man", man))
    application.add_handler(MessageHandler(filters.COMMAND, noop))

    application.run_polling()


if __name__ == "__main__":
    main()
