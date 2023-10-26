import requests
import os

def download_file(url, folder_path):
    response = requests.get(url, stream=True)
    response.raise_for_status()  # проверка на ошибки

    # Получение имени файла из URL
    filename = url.split('/')[-1]
    file_path = os.path.join(folder_path, filename)

    with open(file_path, 'wb') as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)
            
download_file("http://192.168.0.4:8000/download/main.py")