# XBoxParser
![made by](https://img.shields.io/badge/made_by-slychagin-green)
![python](https://img.shields.io/badge/python-v3.10.5-blue)
![bs4](https://img.shields.io/badge/bs4-red)
![selenium](https://img.shields.io/badge/selenium-blue)
![pandas](https://img.shields.io/badge/pandas-green)

Parser get data from XBox games

#### Games parser from https://www.xbox.com/ru-RU/games/all-games
#
Для парсинга данных с данного сайта были использованы Selenium и bs4.
Сначала запускается Selenium, открывает необходимое количество игр, чтобы данные по ним подгрузились, а после скачиваются ссылки по всем играм в необходимом количестве. Затем уже начинает работать bs4 в связке с requests. После парсинга данные сохраняются в csv файл с помощью pandas.

#### Вы можете запустить этот проект локально просто сделав следующее:
- `git clone https://github.com/slychagin/XBoxParser.git`;
- у вас должен быть установлен Python;
- установите все зависимости из файла requirements.txt;
- запустить файл main.py (количество игр, которое необходимо спарсить, можно изменить в файле input_data.py)
