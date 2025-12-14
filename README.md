# Проект: Автоматизированное развертывание ML-модели с CI/CD

## Описание
Этот проект реализует автоматизированное развертывание ML-модели с использованием Docker, GitHub Actions и стратегии Blue-Green Deployment. Модель (линейная регрессия, сохранена в model.pkl) упакована в FastAPI-сервис с эндпоинтами /health (статус и версия) и /predict (инференс). Версия модели передается через ENV MODEL_VERSION.

### Структура
- `app/`: Код приложения (main.py, requirements.txt, model.pkl).
- `Dockerfile`: Для сборки образа.
- `docker-compose.blue.yml` и `docker-compose.green.yml`: Для версий v1.0.0 (blue) и v1.1.0 (green).
- `nginx.conf` и `docker-compose.nginx.yml`: Балансировщик для Blue-Green.
- `.github/workflows/deploy.yml`: CI/CD пайплайн.

### Стратегия развертывания: Blue-Green
- **Blue**: Старая версия (v1.0.0) на порту 8081.
- **Green**: Новая версия (v1.1.0) на порту 8082.
- Трафик изначально на blue (через Nginx). Переключение: измени `proxy_pass` в nginx.conf на `http://green;` и перезапусти `docker-compose -f docker-compose.nginx.yml up -d`.
- Rollback: Верни `proxy_pass` на `http://blue;` и перезапусти Nginx. Тестирование: Проверь /health для обеих (curl http://localhost:8081/health и curl http://localhost:8082/health). Если green нестабильна (ошибки в /health), откати.
- Это позволяет нулевое время простоя и быстрый откат.

### Мониторинг и метрики
- **/health**: Возвращает статус ("ok") и версию модели для проверки стабильности. Метрика: Если статус != "ok", модель нестабильна — откат.
- **Логи**: В main.py добавлено логирование (INFO для успешных запросов, ERROR для ошибок). Просмотр: `docker logs <container_id>`.
- **Версии**: Контролируются через ENV MODEL_VERSION. Откат — переключение на blue.
- Анализ: После деплоя проверяй метрики (response time, error rate) через логи или инструменты вроде Prometheus (не реализовано здесь, но можно добавить).

### Инструкции по запуску (локально, 5 команд)
1. Собери образ: `docker build -t ml-service:v1.0.0 .` (для v1.1.0 измени тег и ENV в Dockerfile).
2. Запусти blue: `docker-compose -f docker-compose.blue.yml up -d`.
3. Запусти green: `docker-compose -f docker-compose.green.yml up -d`.
4. Запусти Nginx: `docker-compose -f docker-compose.nginx.yml up -d`.
5. Проверь: `curl http://localhost/health` (должен вернуть {"status": "ok", "version": "v1.0.0"}).

### Проверка эндпоинтов
- Health: `curl http://localhost/health` → {"status": "ok", "version": "v1.x.x"}.
- Predict: `curl -X POST http://localhost/predict -H "Content-Type: application/json" -d '{"x": [1,2,3]}'` → {"prediction": [результат]}.
- После переключения на green: Повтори проверки, версия изменится на "v1.1.0".

### CI/CD и имитация деплоя
Поскольку в задании не указано конкретное облако и доступ не предоставлен, деплой имитируется в GitHub Runner:
- Workflow (.github/workflows/deploy.yml) собирает Docker-образ, пушит в GHCR с тегом по секрету MODEL_VERSION.
- Имитирует деплой: Запускает контейнер в runner (docker run -d), проверяет /health и /predict через curl к localhost:8080.
- Если проверки fail — workflow падает (аналог rollback).
- Секреты: MODEL_VERSION в GitHub Secrets (не в коде).
- Логи Actions показывают метрики (вывод curl, статусы).