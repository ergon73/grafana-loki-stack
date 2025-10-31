## grafana-loki-stack

Полноценный стек для мониторинга логов на основе Grafana + Loki. Логи отправляются напрямую по HTTP API (без Promtail). В составе есть тестовое Python‑приложение‑симулятор с реалистичными событиями.

### Возможности
- **Loki 2.9.0** — хранилище логов
- **Grafana 10.1.0** — визуализация и дашборды
- **Docker Compose** — развёртывание одной командой
- **Автопровижининг** источника данных Grafana
- **Тестовое приложение** с `send_log_to_loki` и метками: `job`, `level`, `activity`

---

## Требования
- Docker и Docker Compose
- Python 3.8+
- ОС: Windows/macOS/Linux

---

## Порты
- Grafana: `http://127.0.0.1:43000`
- Loki HTTP API: `http://127.0.0.1:43100`

Порты кастомные (43000/43100), чтобы избежать конфликтов на Windows. При необходимости можно изменить их в `docker-compose.yml`.

---

## Структура репозитория
- `grafana-loki-stack/docker-compose.yml` — сервисы `loki` и `grafana`
- `grafana-loki-stack/loki-config.yaml` — конфигурация Loki
- `grafana-loki-stack/grafana-datasource.yaml` — автопровижининг Data Source
- `grafana-loki-stack/app.py` — генератор логов и отправка в Loki
- `requirements.txt` — зависимости Python
- `LICENSE` — лицензия MIT

---

## Быстрый старт

### 1) Запуск контейнеров
```bash
docker compose -f grafana-loki-stack/docker-compose.yml up -d
```

Проверка готовности Loki:
```bash
curl http://127.0.0.1:43100/ready   # ожидаемо: ready
```

### 2) Подключение к Grafana
- Перейдите: `http://127.0.0.1:43000`
- Логин/пароль: `admin`/`admin`
- Источник данных Loki создаётся автоматически (URL `http://127.0.0.1:43100`). При необходимости можно проверить в Grafana: Connections → Data sources → Loki → Save & test.

### 3) Запуск тестового приложения
```bash
python -m venv venv
# Windows PowerShell
./venv/Scripts/Activate.ps1
# Linux/macOS
# source venv/bin/activate

pip install -r requirements.txt
python grafana-loki-stack/app.py
```

Приложение начнёт генерировать события и отправлять их в Loki.

---

## Как это работает

### Отправка логов
`app.py` использует HTTP POST на `/loki/api/v1/push` и формат:

```json
{
  "streams": [
    {
      "stream": { "job": "crypto-app", "level": "INFO", "activity": "system" },
      "values": [["<timestamp_ns>", "<message>"]]
    }
  ]
}
```

Метки (labels):
- `job`: постоянное имя приложения (`crypto-app`)
- `level`: `INFO|ERROR|DEBUG|WARNING|CRITICAL`
- `activity`: `trading|user-activity|system|validation`

### Конфигурация Grafana Data Source
`grafana-loki-stack/grafana-datasource.yaml`:

```startLine:endLine:grafana-loki-stack/grafana-datasource.yaml
apiVersion: 1

datasources:
  - name: Loki
    type: loki
    access: proxy
    url: http://127.0.0.1:43100
    isDefault: true
    jsonData:
      maxLines: 1000
```

---

## Создание дашборда

### Панель 1 — последние логи
Запрос LogQL:
```logql
{job="crypto-app"}
```
Визуализация: Logs (или Table).

### Панель 2 — распределение по уровням
Переключите редактор на «Code» и вставьте:
```logql
sum by (level) (
  count_over_time({job="crypto-app"}[$__interval])
)
```
Визуализация: Pie chart. Рекомендуемые настройки: Legend → Values + Label; Display labels → Name and value.

---

## Типовые запросы LogQL
```logql
# Все логи приложения
{job="crypto-app"}

# Только ошибки
{job="crypto-app", level="ERROR"}

# Фильтр по тексту
{job="crypto-app"} |= "Транзакция"

# Кол-во логов по уровням за 5 минут
sum by (level) (count_over_time({job="crypto-app"}[5m]))
```

---

## Траблшутинг
- «Data source connected, but no labels received» — запустите `app.py` и повторите Save & test.
- Конфликт портов на Windows — измените проброс в `docker-compose.yml` (например, на 43000/43100), перезапустите compose.
- Проверка Loki: `curl http://127.0.0.1:43100/ready` → должно вернуть `ready`.
- Логи контейнеров: `docker compose -f grafana-loki-stack/docker-compose.yml logs -f`

---

## Разработка
- Изменяйте URL Loki в `grafana-loki-stack/app.py` через константу `LOKI_URL`.
- Параметры хранения и индексации — в `grafana-loki-stack/loki-config.yaml`.

---

## Лицензия
MIT — см. `LICENSE`.

