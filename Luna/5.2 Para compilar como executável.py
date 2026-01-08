pip install pyinstaller
pyinstaller --onefile --windowed --icon=assets/luna_icon.ico --add-data "assets;assets" --add-data "config.json;." --add-data "database.json;." main.py