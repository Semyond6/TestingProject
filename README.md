# 1. Клонировать проект
git clone <repository>

# 2. Создать .env файл
cp .env.example .env

# 3. Запустить через Docker Compose
docker-compose up -d

# 4. Или запустить локально
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows
Для тестирования на Windows добавить в requirements.txt psycopg2==2.9.12
pip install -r requirements.txt
python -m app.init_db
python run.py

# 5. Тестовые данные
1. Администратор - admin@gmail.com / Admin123456
2. Пользователь - test@gmail.com / Test123456