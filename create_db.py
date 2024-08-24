import sqlite3

# Conectar a la base de datos (se creará si no existe)
conn = sqlite3.connect('weas.db')
cursor = conn.cursor()

# Crear la tabla producto
cursor.execute('''
CREATE TABLE IF NOT EXISTS producto (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    descripcion TEXT NOT NULL,
    stock INTEGER NOT NULL
)
''')

# Crear la tabla imagenes relacionada con producto
cursor.execute('''
CREATE TABLE IF NOT EXISTS imagen (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    producto_id INTEGER,
    imagen_path TEXT NOT NULL,
    FOREIGN KEY (producto_id) REFERENCES producto (id)
)
''')

# Confirmar los cambios y cerrar la conexión
conn.commit()
conn.close()

print("Base de datos y tablas creadas con éxito.")
