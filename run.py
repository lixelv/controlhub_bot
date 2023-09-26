import subprocess
import requests
from time import sleep
from cnf import link

prev_value = requests.get(link).json()

while True:

    value = requests.get(link).json()

    print(value)

    if value != prev_value and value["run"]:
        try:
            subprocess.run(value["args"])
        except Exception as e:
            print(f"Error {e}")

    prev_value = value

    sleep(value["sleep"])

