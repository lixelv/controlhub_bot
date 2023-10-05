from envparse import env
import requests
import os
import ctypes

def create_hidden_folder(path: str):
    if not os.path.exists(path):
        os.makedirs(path)
        # Установить атрибут скрытой папки
        ctypes.windll.kernel32.SetFileAttributesW(path, 2)

# Получить путь к директории, в которой находится скрипт
script_dir = os.path.dirname(os.path.abspath(__file__))

# Сформировать полный путь к файлу .env
env_path = os.path.join(script_dir, '.env')

env.read_envfile(env_path)

link = env('LINK')
store = os.path.join(script_dir, 'data')

