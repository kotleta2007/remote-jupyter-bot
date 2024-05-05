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

# For all messaging, make lines ~50 columns long.

# get token from environment
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
assert TOKEN is not None

# configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(name)s", level=logging.INFO
)

# Map(Alias -> CID)
running = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    create a local table of notebooks

    Greet the user. 

    Create a new local file that saves 
    the map of names to notebooks.
    By default, this file is called `notebooks.csv`.
    """

    assert update.effective_chat is not None
    # create notebooks.csv for INIT command
    notebooks.CSV_FILEPATH.touch()
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Local table created.")


async def init(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    add a new notebook

    /init ALIAS TYPE → creates new notebook ALIAS of type TYPE

    ALIAS is a short name for your new notebook.
    You will use it with /run.

    TYPE is one of the available types of notebooks.
    You can find the whole list with /ls.
    """
    assert update.effective_chat is not None
    assert context.args is not None

    if len(context.args) != 2:
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text="Provide a notebook name and type."
        )
        return
    
    alias, name = context.args[0], context.args[1]

    if name not in notebook_types:
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text="Invalid notebook type. Consult /ls for available notebook types."
        )
        return

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
    """
    run a notebook

    /run ALIAS → starts an instance of a notebook
    
    ALIAS refers to one of the existing notebooks on your machine.
    These are created by calling the /init command
    and stored in a local CSV file.
    """
    assert update.effective_chat is not None

    if context.args is None or len(context.args) == 0:
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text="Provide a notebook name."
        )
        return
    
    assert len(context.args) == 1
    notebook_name = context.args[0]

    #TODO: check if the cid file already exists
    # this means that the notebook is already running:
    # inform the user about this, send a message, don't create a new instance
    # Later, find out how to handle multiple instances of the same image
    # (multiple instances of a PyTorch notebook)

    # print(f'Running {docker.docker_command}')
    notebook_type = notebooks.get(notebook_name)

    if notebook_type is None:
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text="Notebook doesn't exist. Create it with /init."
        )
        return

    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text=f'Starting notebook: {notebook_name}'
    )

    docker_process = subprocess.Popen(
        ' '.join(docker.run(HOST_PORT=60000, notebook_name=notebook_name, notebook_type=notebook_type)),
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
        running[notebook_name] = pid
    # remove CIDFILE
    pathlib.Path.unlink(docker.CIDFILE)

    await context.bot.send_message(chat_id=update.effective_chat.id, text=f'Your token:')
    await context.bot.send_message(chat_id=update.effective_chat.id, text=output)


async def kill(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    kill a running instance of a notebook

    /kill ALIAS → stops the Docker container for the notebook
    """
    assert update.effective_chat is not None

    if context.args is None or len(context.args) != 1:
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text="Provide a notebook name."
        )
        return

    notebook_name = context.args[0]
    
    global running
    if notebook_name not in running.keys():
        await context.bot.send_message(
            chat_id=update.effective_chat.id, 
            text='No such notebook currently running.'
        )
        return
    
    # kill the docker container
    subprocess.Popen(
        docker.docker_kill_command(running[notebook_name]),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    # remove the key-value pair from the dictionary
    del running[notebook_name]

    response = f"Killed notebook: {notebook_name}"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response)


async def ps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    view currently running Jupyter notebooks

    /ps → return all currently running instances
    """
    assert update.effective_chat is not None
    response = f"Currently running: {running}"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response)

async def ls(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    view available Jupyter notebooks

    /ls → return all types of Jupyter notebooks available to user
    """
    assert update.effective_chat is not None

    response = "Available notebooks:\n"
    response += "\n".join(notebooks.read_all())
 
    response += "\n\nNotebook types:\n"
    response += "\n".join(notebook_types)

    await context.bot.send_message(chat_id=update.effective_chat.id, text=response)

async def noop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    unrecognized command
    """
    assert update.effective_chat is not None
    response = "Unrecognized command. Use /man to get list of commands."
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response)

async def msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    ignore messages
    """
    assert update.effective_chat is not None
    response = "Let's stick to commands! 😃"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response)

async def man(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    describe a command OR list all commands

    /man → list all commands (name, summary)
    /man CMD_NAME → provide full description of command
    """
    assert update.effective_chat is not None
    assert context.args is not None

    match context.args:
        case []:
            response = "Commands:"
            for cmd in cmds:
                assert cmd.__doc__ is not None
                response += f"\n/{cmd.__name__} -- {cmd.__doc__.splitlines()[1]}"
        case [cmd_name] if [x for x in cmds if cmd_name.lstrip("/") == x.__name__]:
            cmd = next(x for x in cmds if cmd_name.lstrip("/") == x.__name__)
            response = f"\n/{cmd.__name__} -- {cmd.__doc__}"
        case [cmd_name]:
            response = "Command not found."
        case _:
            response = "Provide one command."
    
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response)


def main() -> None:
    """Run the bot."""
    application = ApplicationBuilder().token(TOKEN).build()

    for cmd in cmds:
        application.add_handler(CommandHandler(cmd.__name__, cmd))
    application.add_handler(MessageHandler(filters.COMMAND, noop))
    application.add_handler(MessageHandler(None, msg))

    application.run_polling()


if __name__ == "__main__":
    cmds = [start, man, ls, init, run, ps, kill]
    notebook_types = [
        "quay.io/jupyter/minimal-notebook",
        "quay.io/jupyter/scipy-notebook",
        "quay.io/jupyter/pytorch-notebook",
    ]
    main()
