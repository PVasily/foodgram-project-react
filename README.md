# Проект «Foodgram-project-react»

<!-- ![example workflow](https://github.com/Pvasily/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg?event=push) -->

<!-- *Проект доступен по адресу*  [http://51.250.25.69:8888/redoc/](http://51.250.25.69:8888/redoc/)  -->

### Описание

На этом сервисе пользователи смогут публиковать рецепты (__Recipe__), подписываться на публикации других пользователей (__Follow__), добавлять понравившиеся рецепты в список «Избранное» (__Favorite__), а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд (__Cart__).

### Функционал:
*RECIPE*
- Получить список всех рецептов
- Создать новый рецепт
- Открыть страницу рецепта
- Частично обновить свой рецепт
- Удалить свой рецепт

*FOLLOW*
- Подписаться на пользователей и отписаться от них
- Получить список пользователей, на которых создана подписка
- Получить список рецептов этих пользователей

*USER*
- Создать пользователя
- Авторизоваться по токену
- Изменить пароль

*FAVORITE*
- Добавить рецепт в Избранное
- Удалить рецепт из Избранного
- Получить список избранных рецептов

*CART*
- Добавить рецепт в список покупок
- Удалить рецепт из списка покупок
- Выгрузить файл со списком ингредиентов и их количеством, необходимых 
  для приготовления блюд по рецептам из списка покупок

### Установка
__Шаг 1. Проверьте установлен ли у вас Docker__

Прежде, чем приступать к работе, необходимо знать, что Docker установлен. Для этого достаточно ввести:

`docker -v`
или скачайте Docker Desktop для Mac или Windows. Docker Compose будет установлен автоматически. В Linux убедитесь, что у вас установлена последняя версия Compose. Также вы можете воспользоваться официальной инструкцией.

__Шаг 2. Клонируйте репозиторий себе на компьютер__

Введите команду:

`git clone git@github.com:PVasily/foodgram-project-react.git`
__Шаг 3. Создайте в клонированной директории файл .env__

Пример:

DB_ENGINE=django.db.backends.postgresql

DB_NAME=postgres

POSTGRES_USER=postgres

POSTGRES_PASSWORD=postgres

DB_HOST=db

DB_PORT=5432

__Шаг 4. Запуск docker-compose__

Для запуска необходимо выполнить из директории с проектом команду:

`docker-compose up -d`

__Шаг 5. База данных__

Создаем и применяем миграции:

`docker-compose exec web python manage.py makemigrations --noinput`
`docker-compose exec web python manage.py migrate --noinput`

__Шаг 6. Подгружаем статику__

Выполните команду:

`docker-compose exec web python manage.py collectstatic --no-input` 

__Шаг 7. Заполнение базы тестовыми данными__
Для заполнения базы тестовыми данными вы можете использовать файл ingredients.csv, который находится в папке data. Выполните команду:

`docker-compose exec web python manage.py import_csv`

__Другие команды:__

Создание суперпользователя:

`docker-compose exec web python manage.py createsuperuser`

Остановить работу всех контейнеров можно командой:

`docker-compose down`

Для пересборки и запуска контейнеров воспользуйтесь командой:

`docker-compose up -d --build` 

Мониторинг запущенных контейнеров:

`docker stats`

Останавливаем и удаляем контейнеры, сети, тома и образы:

`docker-compose down -v`

__Примеры:__

__Получаем token__

Получаем токен для авторизации (для формирования запросов и ответов использована программа Postman).

Отправляем POST-запрос на адрес `http://127.0.0.1/api/auth/token/login/`

Обязательные поля: `email`, `username`, `password`, `first_name`, `last_name`

__Получение рецептов__

Запрос для получения списка рецептов

Отправляем GET-запрос на адрес `http://127.0.0.1/api/recipes/`.

Получение страницы рецепта 

GET `http://127.0.0.1/api/recipes/<recipe_id>/`

__Добавление рецепта в Избранное__

POST `http://127.0.0.1/api/recipes/<recipe_id>/favorited/`

__Выгрузить файл со cписком покупок__

GET `http://127.0.0.1/api/download_shopping_cart/`
