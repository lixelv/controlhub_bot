import subprocess
import pyautogui
import os

from cnf import link, store, split, download_file, get_data, send_success, send_error
from time import sleep
from pynput.keyboard import Controller

keyboard = Controller()

def run(s: str):
    lst = split(s, ' & ')
    for i in range(len(lst)):
        if lst[i].count(' @* ') != 0:
            lst[i] = s[i].split(' @* ')
            lst[i][1] = int(lst[i][1])
        else:
            lst[i] = [lst[i], 1]

    # разделяем запросы на списки
    lst = [(split(item[0], ', '), item[1]) for item in lst]
    try:
        compile(lst)
        send_success(f"Команда выполнена: {lst}")
        
    except Exception as e:
        send_error(f"Ошибка при выполнении команды: {lst} err: {e}")

def compile(lst: list):
        # запускаем процесс выполнения команд
    for val, times in lst:
        
        for _ in range(times):
            # при установке
            if val[0] == 'download':
                val[1] = val[1].replace('/link/', f'{link}download/')
                download_file(val[1], store)

            # при нажатии клавиши (1)
            elif val[0] == 'press':
                pyautogui.press(val[1])

            # при нажатии клавиш (2 <)
            elif val[0] == 'hotkey':
                pyautogui.hotkey(val[1:])

            # при нажатии мыши
            elif val[0] == 'click':
                pyautogui.click(button=val[1])

            # при вводе текста
            elif val[0] == 'write':
                keyboard.type(', '.join(val[1:]))

            # при задержке
            elif val[0] == 'sleep':
                sleep(float(val[1].replace(',', '.')))

            # для запуска чего-то специфичного
            elif val[0] == 'exec':
                exec(', '.join(val[1:]))

            elif val[0][0] == '@':
                data = get_data(val[0].replace('@', ''))
                run(data)

            # при использовании Popen
            else:
                val[0] = val[0].replace('/user/', f'/{os.getlogin()}/')
                subprocess.Popen(val, shell=True)
