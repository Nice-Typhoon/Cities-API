Тестовое задание - HTTP API для хранения, добавления и поиска городов по заданной точке. 

Можно:
- Добавить город по названию - координаты подтягиваются автоматически через OpenStreetMap Nominatim (бесплатно, без API-ключа)
- Удалить город по ID
- Получить список всех городов с пагинацией
- Найти N ближайших городов к произвольной точке на карте

Стек
- FastAPI - HTTP-сервер
- SQLAlchemy + asyncpg - работа с базой данных
- PostgreSQL + PostGIS - хранилище с поддержкой геопространственных запросов
- Alembic - миграции схемы БД
- httpx - HTTP-клиент для геокодинга
- Pydantic- валидация данных и конфигурация

запуск:
создать .env или скопировать .env.example

docker-compose up --build


документация Swagger: http://localhost:8000/docs

При первом запуске entrypoint.sh дожидается готовности postgres и автоматически прогоняет миграции - вручную ничего делать не нужно.
Без него бы приложение пыталось бы совершить подключение к бд, которая ещё не развернута


Эндпоинты

```
POST   /api/v1/cities              Добавить город
GET    /api/v1/cities              Список городов (?offset=0&limit=100)
GET    /api/v1/cities/{id}         Получить город по ID
DELETE /api/v1/cities/{id}         Удалить город
GET    /api/v1/cities/nearest      Найти ближайшие (?latitude=60.17&longitude=24.94&limit=2)
```

Пример добавления города:

```bash
curl -X POST http://localhost:8000/api/v1/cities \
  -H "Content-Type: application/json" \
  -d '{"name": "Helsinki"}'
```

Пример поиска ближайших:

```bash
curl "http://localhost:8000/api/v1/cities/nearest?latitude=60.5&longitude=25.0&limit=2"
```

Ответ:

```json
[
  {
    "id": 1,
    "name": "Helsinki",
    "latitude": 60.169857,
    "longitude": 24.938379,
    "distance_m": 38423.5
  },
  {
    "id": 3,
    "name": "Tallinn",
    "latitude": 59.436962,
    "longitude": 24.753574,
    "distance_m": 91200.1
  }
]
```


Поиск ближайших городов:

Используется PostGIS, расширение postgres, с gist-индексом и KNN-оператором `<->`. Он обходит дерево и находит ближайшие точки за O(log n) без сканирования всей таблицы. Расстояние считается как геодезическое (по поверхности Земли) в метрах, а не в градусах.

Запросы к PostGIS намеренно написаны напрямую через asyncpg, минуя ORM чтобы уменьшить задержку поиска в раза 2 примерно

Архитектура

Проект разбит на слои, каждый знает только о соседнем:

1. HTTP (эндпоинты)
2. Service (бизнес-логика)
3. Repository (работа с данными)
4. Database (PostgreSQL)


Геокодинг вынесен в отдельный сервис с Protocol-интерфейсом - в тестах он заменяется фейком без сети. Все зависимости (пул соединений, HTTP-клиент, фабрика сессий) живут на app.state и создаются один раз при старте через lifespan.

Переменные окружения

| Переменная| По умолчанию | Описание |
|---|---|---|
| `DB_HOST` | `localhost` | Хост PostgreSQL |
| `DB_PORT` | `5432` | Порт |
| `DB_NAME` | `cities_db` | Название базы |
| `DB_USER` | `postgres` | Пользователь |
| `DB_PASSWORD` | `postgres` | Пароль |
| `DB_POOL_SIZE` | `20` | Размер пула соединений |
| `GEOCODING_BASE_URL` | `https://nominatim.openstreetmap.org` | Geocoding API |
| `GEOCODING_TIMEOUT` | `10.0` | Таймаут запроса (сек) |
| `DEBUG` | `false` | Включает SQL-логирование |
