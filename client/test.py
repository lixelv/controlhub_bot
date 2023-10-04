import re
import subprocess
import pyautogui
from scripts import *
from time import sleep
from pynput.keyboard import Controller

keyboard = Controller()

def parse_command(s: str):
    parsed_commands = []
    i = 0
    while i < len(s):
        if s[i] == '(':
            j = i
            balance = 0  # счетчик скобок для обработки вложенности
            while j < len(s) and (balance > 0 or s[j] != ')'):
                if s[j] == '(': balance += 1
                if s[j] == ')': balance -= 1
                j += 1
            command = s[i + 1:j]  # извлекаем команду из скобок
            i = j + 1  # обновляем индекс для следующей итерации
        else:
            # если скобки отсутствуют, считываем команду до символов ` & ` или ` @* `
            j = s.find(' & ', i)
            k = s.find(' @* ', i)
            if j == -1 and k == -1:
                command = s[i:]
                i = len(s)
            elif j != -1 and (k == -1 or j < k):
                command = s[i:j]
                i = j
            else:
                command = s[i:k]
                i = k

        multiplier = 1  # по умолчанию множитель равен 1
        if i < len(s) and s[i:i + 3] == ' @* ':
            j = s.find(' ', i + 3)
            if j == -1:
                multiplier = int(s[i + 3:])
                i = len(s)
            else:
                multiplier = int(s[i + 3:j])
                i = j

        parsed_commands.append((command.split(', '), multiplier))

        # пропускаем символы ` & ` для следующей команды
        if i < len(s) and s[i:i + 3] == ' & ':
            i += 3

    return parsed_commands

print(parse_command('(print, Hello & Hi!) @* 5'))
