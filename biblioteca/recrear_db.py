import psycopg

conn = psycopg.connect("postgresql://postgres:1234@localhost:5432/postgres", autocommit=True)
# Terminar conexiones activas a la BD
conn.execute(
    "SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
    "WHERE datname = 'biblioteca' AND pid <> pg_backend_pid()"
)
conn.execute("DROP DATABASE IF EXISTS biblioteca")
conn.execute("CREATE DATABASE biblioteca")
conn.close()
print("Base de datos 'biblioteca' recreada exitosamente")
