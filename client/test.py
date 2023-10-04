import requests
import threading

def get_data(json):
    response = requests.post('http://localhost:8001/', json=json)
    print(response.json())

tasks = []

for i in range(100):
    tasks.append(threading.Thread(target=get_data, args=({"args": i},)))

for i in tasks:
    i.start()
