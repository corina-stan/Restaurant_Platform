#!/sh

echo "Waiting for database..."

# Wait for database using python socket check (always works since Python is installed)
python << END
import socket
import time
import os

db_host = os.environ.get('DB_HOST', 'localhost')
db_port = int(os.environ.get('DB_PORT', 5432))

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
while True:
    try:
        s.connect((db_host, db_port))
        s.close()
        print("Database connected successfully!")
        break
    except socket.error:
        print("Database not available yet, sleeping...")
        time.sleep(2)
END

echo "Database is ready! Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting ASGI server (Daphne)..."
exec daphne -b 0.0.0.0 -p 8000 config.asgi:application
