# Description
The bot's task is to collect data from the table and display it in a telegram in a readable form

[![Demo](https://img.youtube.com/vi/fSNrtCuDQxo/0.jpg)](https://www.youtube.com/watch?v=fSNrtCuDQxo)

# Install
``` 
mkdir vapeshopbot
```
Move all files to vapeshopbot folder
```
rm -rf venv
python -m venv "env"
source env/bin/activate
pip3 install -r requirements.txt
```
# Run
Create "profiles" dir, then "production.py" and set next variables:
```
owner = 'owner id tg'
welcome_message = 'welcome message for users' 
token = 'bot token'
spreadsheet_id = 'spreadsheet id google sheets'
```
```
python main.py
```
For production run as system daemon
