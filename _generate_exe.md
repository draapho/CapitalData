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
