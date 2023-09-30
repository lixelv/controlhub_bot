import os
import subprocess
from time import sleep
from cnf import *


def send_error(error: str) -> None:
    try:
        url = f'{link}error'
        requests.post(url, json={"error": error})

    except Exception as e:
        print(e)

def send_success(success: str) -> None:
    try:
        url = f'{link}success'
        response = requests.post(url, json={"task": success})
        if response.status_code != 204:
            print(f"Error: {response.text}")

    except Exception as e:
        print(e)

while True:
    try:
        prev_value = requests.get(link).json()
        break
    except Exception as e:
        print(e)
        sleep(20)


while True:

    try:
        value = requests.get(link).json()

        print(value)

        if value["run"] != prev_value["run"] and value["run"]:
            try:
                value["args"][0] = value["args"][0].replace('/user/', f'/{os.getlogin()}/')
                subprocess.Popen(value["args"])
                send_success(f"Команда выполнена: {value['args']}")

            except Exception as e:
                send_error(f"Ошибка при выполнении команды: {e}")

        prev_value = value
        sleep(value["sleep"])

    except Exception as e:
        send_error(f"Общая ошибка: {e}")
        sleep(20)
