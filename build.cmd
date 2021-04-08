rmdir /S /Q dist
pipenv run pyinstaller ^
--window --onefile --icon=images\icon.ico ^
--add-data="images\*;images" ^
conntester.py
rmdir /S /Q build
del conntester.spec
copy conntester.ini dist\
