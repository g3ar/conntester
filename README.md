# Conntester
## About
This is simple, small, crossplatform tool for monitoring internet 
connection quality. Develped using python, pyqt5.
![image](https://user-images.githubusercontent.com/6010030/114169560-66654d80-993a-11eb-9c1f-66e859a8c032.png)
## Run from binary
Unpack release to any directory you want, edit conntester.ini to 
fit your needs and run conntester binary.
### Linux run
In linux you must allow raw sockets for conntester binary.
```
sudo setcap cap_net_raw+ep /path/to/conntester.bin
```
## Run from source
```
git clone https://github.com/g3ar/conntester.git
cd conntester
pipenv --python 3.7
pipenv shell
pipenv install --dev
python ./conntester.py
```
## TODO
* Add notifications on quality change
## License
GPLv3
