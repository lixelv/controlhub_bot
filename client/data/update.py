import os

from icecream import ic
from shutil import move

slash = '\\'
main_dir = '/'.join(__file__.split(slash)[:-1])

with open(f'{main_dir}/dont_touch.txt', 'r') as file:
    dont_touch_files = [i.replace('\n', '') for i in file.readlines()]

for file in os.listdir(f"{main_dir}/.."):
    if os.path.splitext(file)[1] == '.py' and __file__.split(slash)[-1] not in dont_touch_files:
        try:
            move(f"{main_dir}/{file}", f"{main_dir}/../{file}")
        except Exception as e:
            ic(e)
