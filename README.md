# AmChamRuBot 🌐

Навигатор по мероприятиям и каналам AmCham Russia. Двуязычное меню, трекинг нажатий и активностей (SQLite).

## Функции
- RU/EN меню, быстрые ссылки на разделы/каналы
- Логирование действий пользователей в SQLite
- Команда /track_users для администраторов

## Запуск
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp config.py.example config.py
python AmChamBot.py
```
