import os
from cnf import *
import os

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