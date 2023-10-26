import os

from icecream import ic
from shutil import move

slash = '\\'
main_dir = '/'.join(__file__.split(slash)[:-1])
for file in os.listdir(ic(f"{main_dir}/..")):
    if os.path.splitext(file)[1] == '.py':
        try:
            move(ic(f"{main_dir}/{file}", f"{main_dir}/../{file}"))
        except Exception as e:
            ic(e)
