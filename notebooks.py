import csv
import pathlib

CSV_FILEPATH = pathlib.Path('~/git/remote-jupyter-bot/notebooks.csv').expanduser()

def put(alias, image):
    not_found = get(alias) is None
    if not_found:
        with open(CSV_FILEPATH, 'a') as file:
            writer = csv.writer(file)
            writer.writerow([alias, image])
    return not_found

def get(alias):
    with open(CSV_FILEPATH, 'r') as file:
        reader = csv.reader(file)
        return next((line[1] for line in reader if line[0] == alias), None)

# design special keyboard for choosing correct type of notebook
