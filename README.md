# Документация к функции `comppile`

Функция `comppile` предназначена для обработки строковых команд и выполнения соответствующих действий на вашем компьютере. Каждая команда в строке должна быть разделена символами ` & `. Параметры внутри команды разделяются символами `, ` (запятая и пробел).

## Формат команды

Каждая команда имеет следующий формат:

```plaintext
команда, параметр1, параметр2, ..., параметрN
```

Если требуется выполнить команду несколько раз, используйте следующий формат:

```plaintext
команда, параметр1, параметр2, ..., параметрN @* количество_повторений
```

## Примеры команд

Для демонстрации возможностей функции `comppile` ниже приведены некоторые примеры команд.

1. **Загрузка файла:**
   ```plaintext
   download, /link/имя_файла.txt
   ```

2. **Нажатие клавиши:**
   ````plaintext
   press, enter
   ```

3. **Нажатие комбинации клавиш:**
   ````plaintext
   hotkey, ctrl, c
   ```

4. **Клик мышью:**
   ````plaintext
   click, left
   ```

5. **Ввод текста:**
   ````plaintext
   write, Привет, мир!
   ```

6. **Задержка:**
   ````plaintext
   sleep, 2.5
   ```

7. **Выполнение произвольного кода:**
   ```plaintext
   eval, print("Привет, мир!")
   ```

8. **Запуск внешней программы:**
   ````plaintext
   /path/to/program.exe, --option, value
   ```

## Пример строки с командами

````plaintext
download, /link/file.txt & press, enter & write, Привет, мир! & sleep, 1.5 & eval, print("Команда выполнена")
```

Эта строка будет обработана функцией `comppile` так, что сначала будет загружен файл, затем нажата клавиша Enter, введен текст "Привет, мир!", выполнена задержка в 1.5 секунды, и, наконец, будет выполнен произвольный код, выводящий сообщение "Команда выполнена".
