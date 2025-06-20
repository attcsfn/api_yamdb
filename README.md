# Проект YaMDb: Отзывы пользователей на произведения

Проект YaMDb является платформой для сбора и оценки отзывов пользователей на различные произведения, такие как книги, фильмы и музыка. Этот README файл предоставляет обзор проекта и инструкции по запуску.

## Разработчики

[BelikovDenis](https://github.com/BelikovDenis) разрабатывал:
  - систему регистрации и аутентификации;
  - права доступа;
  - работу с токеном;
  - систему подтверждения через e-mail.

[bodary2905](https://github.com/bodary2905) разрабатывал:
  - отзывы;
  - комментарии;
  - рейтинг произведений.

[Borisov Aleksey (attcsfn)](https://github.com/attcsfn) разрабатывал:
  - произведения;
  - категории;
  - жанры;
  - импорт данных из csv файлов.


## Запуск проекта

Клонировать репозиторий и перейти в него в командной строке:

```
https://github.com/attcsfn/api_yamdb.git
```

```
cd api_yamdb
```

Создать и активировать виртуальное окружение:

```
python -m venv venv
```

```
source venv/Scripts/activate
```

Установить зависимости из файла requirements.txt:

```
python -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

Создать файл .env по примеру .env.sample в корне проекта


Создать и выполнить миграции:
```
python manage.py makemigrations
```
python manage.py migrate
```

Запустить проект:

```
python manage.py runserver
```
