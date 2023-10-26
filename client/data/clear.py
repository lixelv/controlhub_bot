import os

from icecream import ic

slash = '\\'
main_dir = '/'.join(__file__.split(slash)[:-1])

with open(f'{main_dir}/dont_touch.txt', 'r') as file:
    dont_touch_files = [i.replace('\n', '') for i in file.readlines()]
    
for file in os.listdir(main_dir):
    if file not in dont_touch_files:
        os.remove(ic(f"{main_dir}/{file}"))