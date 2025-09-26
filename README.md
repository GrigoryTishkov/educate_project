# Posts Analytics

Система для анализа постов пользователей из JSONPlaceholder API.

## Запуск проекта


# Клонируйте репозиторий и перейдите в директорию проекта
```bash
git clone https://github.com/GrigoryTishkov/educate_project.git
cd project
```
# Запустите одной командой:
```bash
./run.sh
```

# Посмотреть на результат можно выполнив команды:
```bash
docker exec -it posts_analitycs_etl bash
psql -U postgres -d postgres
SELECT * FROM raw_users_by_posts LIMIT 5;
SELECT * FROM top_users_by_posts LIMIT 5;
```
# Другим способом после запуска контейнера можно открыть браузер по адресу

```
http://localhost:8080/top
```
