prepare the `version.txt` `user.ico`

run:
```
pyinstaller.exe --onefile --windowed capital.py
pyinstaller.exe --windowed capital.py
```


generate python UI from xxx.ui file
```
pyuic5.exe -x -o gui_main.py gui_main.ui
pyuic5.exe -x -o gui_sub.py gui_sub.ui
```

pip list
```
Package         Version         
--------------- ----------              
APScheduler     3.5.3                  
lxml            4.3.3                              
numpy           1.15.4          
pandas          0.23.4          
PyQt5           5.12.2          
PyQt5-sip       4.19.14         
pyqt5-tools     5.11.3.1.4      
pyqtgraph       0.10.0           
requests        2.21.0                  
tendo           0.2.12          # need to del import in class, otherwise raise error!
```   