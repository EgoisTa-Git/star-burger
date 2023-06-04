# Сайт доставки еды Star Burger

Это сайт сети ресторанов Star Burger. Здесь можно заказать превосходные бургеры с доставкой на дом.

![скриншот сайта](https://dvmn.org/filer/canonical/1594651635/686/)


Сеть Star Burger объединяет несколько ресторанов, действующих под единой франшизой. У всех ресторанов одинаковое меню и одинаковые цены. Просто выберите блюдо из меню на сайте и укажите место доставки. Мы сами найдём ближайший к вам ресторан, всё приготовим и привезём.

На сайте есть три независимых интерфейса. Первый — это публичная часть, где можно выбрать блюда из меню, и быстро оформить заказ без регистрации и SMS.

Второй интерфейс предназначен для менеджера. Здесь происходит обработка заказов. Менеджер видит поступившие новые заказы и первым делом созванивается с клиентом, чтобы подтвердить заказ. После оператор выбирает ближайший ресторан и передаёт туда заказ на исполнение. Там всё приготовят и сами доставят еду клиенту.

Третий интерфейс — это админка. Преимущественно им пользуются программисты при разработке сайта. Также сюда заходит менеджер, чтобы обновить меню ресторанов Star Burger.

### Тестовый вариант сайта

Тестовая версия сайта развернута тут: [Devman-Burgers.RU](https://devman-burgers.ru/)

## Как запустить сайт

Пример показан на основе **ОС Ubuntu**:

Обновите пакеты, установите Git и Docker:
```shell
apt update && apt install git docker
```

Скачайте код:
```sh
git clone https://github.com/devmanorg/star-burger.git
```

Желательно проекты размещать в /opt/ ([вот почему](https://unix.stackexchange.com/questions/11544/what-is-the-difference-between-opt-and-usr-local)).

Перейдите в каталог проекта:
```sh
cd /opt/star-burger
```

Создайте `.env`-файл и пропишите переменные:

- `DEBUG` — дебаг-режим. Поставьте `False`.
- `SECRET_KEY` — секретный ключ проекта. Он отвечает за шифрование на сайте. Например, им зашифрованы все пароли на вашем сайте. Ключ можно получить [тут](https://djecrety.ir/)
- `ALLOWED_HOSTS` — [см. документацию Django](https://docs.djangoproject.com/en/3.1/ref/settings/#allowed-hosts)
- `YANDEX_GEO_APIKEY` - ключ от API Яндекс-геокодера ([инструкция тут](https://dvmn.org/encyclopedia/api-docs/yandex-geocoder-api/)).
- `ROLLBAR_ENABLED` - флаг подключения системы мониторинга ROLLBAR.
- `ROLLBAR_ACCESS_TOKEN` - токен от системы мониторинга ROLLBAR ([инструкция тут](https://docs.openreplay.com/en/integrations/rollbar/)).
- `ROLLBAR_ENVIRONMENT` - название окружения или инсталляции сайта (`development` или `production`).
- `YOUR_DOMAIN` - домен Вашего сайта (например `your_domain.ru`).
- `DOMAIN_NAME` - доменное имя сайта (например `your_domain`).
- `DB_ENGINE` - выбранная БД (данная сборка работает на PostgreSQL - `django.db.backends.postgresql`).
- `DB_NAME` - имя БД для подключения.
- `DB_USER` - имя пользователя БД.
- `DB_PASSWORD` - пароль к БД.
- `DB_HOST` - адрес подключения к БД. Тут задается имя сервиса - необходимо указать `db`.
- `DB_PORT` - порт подключения к БД. Для подключения необходимо указать `5432`.

Разместите файлы ssl-сертификатов и ключа в каталоге `/opt/star-burger/nginx/ssl`:

Файл `your_domain.crt` должен иметь вид:
```sh
-----BEGIN CERTIFICATE-----
#Ваш сертификат#
-----END CERTIFICATE-----
-----BEGIN CERTIFICATE-----
#Промежуточный сертификат#
-----END CERTIFICATE-----
-----BEGIN CERTIFICATE-----
#Корневой сертификат#
-----END CERTIFICATE-----
```

Где:

`your_domain.ru` — домен сайта

`./nginx/ssl/your_domain.crt` — путь до созданного файла с тремя сертификатами

`./nginx/ssl/your_domain.key` — путь до файла с приватным ключом

Запустите сборку контейнеров:

```shell
docker-compose up -d --build
```

Примените миграции в таком порядке:
```shell
docker-compose exec web python manage.py migrate auth --noinput
```
```shell
docker-compose exec web python manage.py migrate admin --noinput
```
```shell
docker-compose exec web python manage.py migrate contenttypes --noinput
```
```shell
docker-compose exec web python manage.py migrate sessions --noinput
```
```shell
docker-compose exec web python manage.py migrate foodcartapp --noinput
```
```shell
docker-compose exec web python manage.py migrate address --noinput
```

Соберите заново статику:
```shell
docker-compose exec web python manage.py collectstatic --no-input --clear
```

## Быстрое обновление кода на сервере

Для быстрого обновления кода на сервере используйте скрипт `deploy_starburger.sh`:
```bash
#!/bin/bash
set -Eeuo pipefail
cd /opt/star-burger/
docker-compose down
git pull
docker-compose up -d --build
docker-compose exec web python manage.py migrate --noinput
docker-compose exec web python manage.py collectstatic --no-input --clear

if [ -f .env ]; then
  export $(echo $(cat .env | sed 's/#.*//g'| xargs -0) | envsubst)
fi

LOCAL_USERNAME=$(whoami)
REVISION=$(git rev-parse --short HEAD)

echo "Code version is:" "$REVISION"
echo "Environment:" "$ROLLBAR_ENVIRONMENT"

curl https://api.rollbar.com/api/1/deploy/ \
  -F access_token="$ROLLBAR_ACCESS_TOKEN" \
  -F environment="$ROLLBAR_ENVIRONMENT" \
  -F revision="$REVISION" \
  -F local_username="$LOCAL_USERNAME"

printf "\nDeploy completed!\n"
```

## Цели проекта

Код написан в учебных целях — это урок в курсе по Python и веб-разработке на сайте [Devman](https://dvmn.org). За основу был взят код проекта [FoodCart](https://github.com/Saibharath79/FoodCart).

Где используется репозиторий:

- Второй и третий урок [учебного курса Django](https://dvmn.org/modules/django/)
