import subprocess
import os
from time import sleep
from cnf import *

prev_value = requests.get(link).json()

while True:

    value = requests.get(link).json()
    
    print(value)

    if value != prev_value and value["run"]:
        try:
            value["args"][0] = value["args"][0].replace('/user/', f'/{os.getlogin()}/')

            subprocess.run(value["args"])

        except Exception as e:
            print(f"Error {e}")

    prev_value = value

    sleep(value["sleep"])

