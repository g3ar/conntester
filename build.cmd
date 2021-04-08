rmdir /S /Q dist
pipenv run pyinstaller ^
--window --onefile --icon=icon.ico ^
--add-data="icon.png;." ^
conntester.py
rmdir /S /Q build
del conntester.spec
copy conntester.ini dist\
