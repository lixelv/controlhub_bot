@echo off

:: Устанавливаем Python-библиотеки
pip install -r lib.txt

:: Создаём ярлык для run.bat
echo Set oWS = WScript.CreateObject("WScript.Shell") > CreateShortcut.vbs
echo sLinkFile = "%~dp0run-server.lnk" >> CreateShortcut.vbs
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> CreateShortcut.vbs
echo oLink.TargetPath = "%~dp0run.bat" >> CreateShortcut.vbs
echo oLink.Save >> CreateShortcut.vbs
cscript CreateShortcut.vbs
del CreateShortcut.vbs

:: Перемещаем ярлык в автозагрузку
move "%~dp0run-server.lnk" "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
