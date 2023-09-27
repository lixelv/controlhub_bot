import db
import json

sql = db.SQLite('db.db')

print(sql.api_read())
with open('main.json', 'r') as file:
    default = json.load(file)

print({"args": [1, 2, 3]}.update(default))
