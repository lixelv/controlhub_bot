import subprocess
import pyautogui
import os

from cnf import link, store, split, download_file, get_data, send_success, send_error
from time import sleep
from pynput.keyboard import Controller

keyboard = Controller()

def compile(s: str):
    try:
        # разделяем запрос по символам ` & `
        s = split(s, ' & ')

        for i in range(len(s)):
            if s[i].count(' @* ') != 0:
                s[i] = s[i].split(' @* ')
                s[i][1] = int(s[i][1])
            else:
                s[i] = [s[i], 1]

        # разделяем запросы на списки
        s = [(split(item[0], ', '), item[1]) for item in s]


        # запускаем процесс выполнения команд
        for val, times in s:
            try:
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
                        compile(data)


                    # при использовании Popen
                    else:
                        val[0] = val[0].replace('/user/', f'/{os.getlogin()}/')
                        subprocess.Popen(val, shell=True)

                send_success(f"Команда выполнена: {val}")

            except Exception as e:
                send_error(f"Ошибка при выполнении команды: {e}")

        # отправляем отчет об ошибке
    except Exception as e:
        send_error(f"Ошибка при выполнении команды: {e}")
