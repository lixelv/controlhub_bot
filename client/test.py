# import PySimpleGUI as sg
# import os
# import re

# # Функция для сохранения REGION в .env файл
# def save_to_env(region_id):
#     env_path = ".env"
#     pattern = re.compile(r'^REGION=.*$', re.MULTILINE)

#     if os.path.exists(env_path):
#         with open(env_path, "r+") as f:
#             content = f.read()
#             content = pattern.sub(f"REGION={region_id}", content) if pattern.search(content) else content + f"\nREGION={region_id}\n"
#             f.seek(0)
#             f.truncate()
#             f.write(content)
#     else:
#         with open(env_path, "w") as f:
#             f.write(f"REGION={region_id}\n")
#     # Вместо всплывающего окна, просто печатаем сообщение в консоль
#     print(f"ID сохранен: {region_id}")

# # Настройка внешнего вида окна
# sg.theme('Dark')   # Выбор темы с серо-синими тонами

# # Создание элементов интерфейса
# layout = [
#     [sg.Text('Введите ваш ID')],
#     [sg.InputText(key='-ID-')],
#     [sg.Button('Сохранить', bind_return_key=True)]
# ]

# # Создание окна
# window = sg.Window('Установка ID', layout, size=(200, 100))

# while True:
#     event, values = window.read()
#     if event == sg.WIN_CLOSED:
#         break
#     if event == 'Сохранить':
#         region_id = values['-ID-']
#         if region_id:
#             save_to_env(region_id)
#             # Очистка поля ввода после сохранения без всплывающего сообщения
#             window['-ID-'].update('')

# window.close()

#print("РАЗРАБОТКА TELEGRAM БОТА НА PYTHON ДЛЯ ОДНОВРЕМЕННОГО УПРАВЛЕНИЯ МНОЖЕСТВОМ КОМПЬЮТЕРОВ С ПОМОЩЬЮ ИНТУИТИВНО ПОНЯТНЫХ ЭЛЕМЕНТОВ УПРАВЛЕНИЯ".lower())
from cnf import get_data

print(get_data(151))