import zipfile
import os
import sys


def unpack_and_delete(zip_path):
    try:
        # Получаем путь к директории, где находится архив
        extract_path = os.path.dirname(zip_path)

        # Распаковка архива
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_path)
        print(f"Архив {zip_path} успешно распакован в {extract_path}")

        # Удаление архива
        os.remove(zip_path)
        print(f"Архив {zip_path} успешно удален")

    except zipfile.BadZipFile:
        print(f"Ошибка: файл {zip_path} не является архивом zip или архив поврежден")
    except Exception as e:
        print(f"Ошибка: {e}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Использование: python unpack.py path_of_zip")
        sys.exit(1)

    zip_path = sys.argv[1]
    unpack_and_delete(zip_path)