# Проект: Автоматизированное Развертывание ML-Модели с Blue-Green Стратегией

## Описание
Этот проект реализует задание по модулю 3 "Автоматизированное развертывание с помощью CI/CD". Выбрана стратегия **Blue-Green Deployment** для безопасного развертывания ML-модели. 

- **Модель**: LogisticRegression (из scikit-learn), обученная на данных с 4 признаками (features). Модель сохранена в `app/model.pkl`.
- **API**: REST с FastAPI. Эндпоинты: `/health` (статус и версия) и `/predict` (инференс, ожидает JSON с полем "x" — список из 4 floats).
- **Версии**: Blue — v1.0.0 (стабильная), Green — v1.1.0 (новая).
- **Балансировщик**: Nginx для переключения трафика.
- **CI/CD**: GitHub Actions для сборки, пуша в GHCR и симуляции деплоя (реальный деплой в облако не реализован из-за отсутствия CLOUD_TOKEN; вместо этого симулируется локальный запуск в Actions).
- **Контейнеризация**: Docker с минимальным образом python:3.11-slim.

Проект протестирован локально. После деплоя (симуляции) проверены эндпоинты с версией модели.

## Структура Репозитория
ml-deployment-project/
├── app/
│   ├── main.py          # Код API-сервиса (FastAPI)
│   ├── model.pkl        # Обученная модель (LogisticRegression с 4 фичами)
│   └── requirements.txt # Зависимости (fastapi, uvicorn, scikit-learn, joblib)
├── .github/
│   └── workflows/
│       └── deploy.yml   # Workflow для CI/CD (сборка, пуш, симуляция деплоя)
├── docker-compose.blue.yml  # Blue версия (v1.0.0)
├── docker-compose.green.yml # Green версия (v1.1.0)
├── Dockerfile           # Файл для сборки Docker-образа
├── nginx.conf           # Конфигурация Nginx для балансировки трафика
└── README.md            # Этот файл с документацией

## Требования
- Docker и docker-compose установлены.
- GitHub-аккаунт для CI/CD (добавьте секреты: `MODEL_VERSION` = "v1.1.0").

## Локальный Запуск и Тестирование
### Шаг 1: Сборка Docker-образа
1. Соберите образ для версии v1 (или укажите тег по версии):
docker build -t ml-service:v1 .

### Шаг 2: Запуск Blue и Green версий
2. Запустите Blue (v1.0.0):
docker-compose -f docker-compose.blue.yml up -d

3. Запустите Green (v1.1.0):
docker-compose -f docker-compose.green.yml up -d

### Шаг 3: Запуск Nginx (балансировщик)
4. Запустите Nginx (изначально трафик на Blue):
docker run -d -p 80:80 -v $(pwd)/nginx.conf:/etc/nginx/nginx.conf nginx

### Шаг 4: Проверка Эндпоинтов
5. Проверьте /health (через Nginx, ожидается версия из nginx.conf):
curl http://localhost/health

Ожидаемый ответ: `{"status": "ok", "version": "v1.0.0"}` (или v1.1.0 после переключения).

6. Проверьте /predict (POST-запрос с 4 фичами, так как модель ожидает именно 4):
curl -X POST http://localhost/predict 

-H "Content-Type: application/json" 

-d '{"x": [1, 2, 3, 4]}'

Ожидаемый ответ: `{"prediction": [класс, например, 0 или 1]}` (зависит от модели и данных).

Если порт занят, убейте процесс: `kill $(lsof -t -i:80)` (или соответствующий порт).

## Стратегия Развертывания: Blue-Green
- **Blue**: Стабильная версия (v1.0.0) на порту 8081.
- **Green**: Новая версия (v1.1.0) на порту 8082.
- **Переключение трафика**: Измените `upstream backend` в `nginx.conf` (с 8081 на 8082) и перезапустите Nginx:
docker stop <nginx_container_id> && docker run -d -p 80:80 -v $(pwd)/nginx.conf:/etc/nginx/nginx.conf nginx

- **Откат (Rollback)**: Верните upstream на 8081 в `nginx.conf` и перезапустите Nginx. Это позволяет мгновенно вернуться к стабильной версии при ошибках.
- **Мониторинг**: Эндпоинт /health возвращает статус и версию. Логи: `docker logs <container_name>`. Метрики: Версия модели через переменную окружения MODEL_VERSION. Стабильность проверяется путём сравнения ответов /predict до и после переключения.

Стратегия протестирована: обе версии доступны одновременно, переключение работает без downtime, откат — мгновенный.

## CI/CD через GitHub Actions
- Файл: `.github/workflows/deploy.yml`.
- Триггер: Пуш в main.
- Шаги: 
- Сборка Docker-образа.
- Пуш в GitHub Container Registry (GHCR).
- Симуляция деплоя (локальный запуск контейнера в Actions с проверкой /health и /predict).
- Секреты: Добавьте в GitHub Settings > Secrets:
- `MODEL_VERSION` (например, "v1.1.0").
- `GITHUB_TOKEN` (генерируется автоматически).
- Реальный деплой в облако симулирован из-за отсутствия CLOUD_TOKEN. В production замените на API-вызов (например, Heroku).

При пушe в main workflow запустится автоматически. Проверьте логи в GitHub > Actions.

## Проверка Результата
- После локального запуска: Используйте команды выше для /health и /predict.
- После симуляции в Actions: Логи покажут вывод curl (успешные ответы).

## Скриншоты
