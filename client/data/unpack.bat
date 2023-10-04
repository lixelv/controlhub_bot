@echo off
setlocal

:: Проверка на наличие аргумента
if "%~1"=="" (
    echo Использование: unpack.bat path_of_zip
    exit /b 1
)

:: Путь к архиву
set "zip_path=%~1"

:: Путь к папке
for %%i in ("%zip_path%") do set "extract_path=%%~dpi"

:: Распаковка архива
7z x "%zip_path%" -o"%extract_path%"

:: Проверка успешности распаковки и удаление архива
if %errorlevel%==0 (
    echo Архив %zip_path% успешно распакован в %extract_path%
    del "%zip_path%"
    echo Архив %zip_path% успешно удален
) else (
    echo Ошибка при распаковке архива
)

endlocal
