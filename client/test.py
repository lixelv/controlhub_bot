import requests

r = requests.post('http://localhost:8001/', json={"a": 1, "b": 2})
print(r.json())
