from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import sqlite3
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

DATABASE = 'weas.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM producto')
    productos = cursor.fetchall()
    conn.close()

    # Obtener la lista de imágenes para cada producto
    product_images = {}
    for producto in productos:
        product_folder = os.path.join(app.config['UPLOAD_FOLDER'], str(producto['id']))
        if os.path.exists(product_folder):
            images = os.listdir(product_folder)
            if images:
                product_images[producto['id']] = images[0]  # Solo la primera imagen
            else:
                product_images[producto['id']] = None

    return render_template('index.html', productos=productos, product_images=product_images)

@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        descripcion = request.form['descripcion']
        stock = request.form['stock']
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO producto (descripcion, stock) VALUES (?, ?)', (descripcion, stock))
        conn.commit()
        producto_id = cursor.lastrowid
        conn.close()
        
        # Crear una carpeta para el producto
        product_folder = os.path.join(app.config['UPLOAD_FOLDER'], str(producto_id))
        os.makedirs(product_folder, exist_ok=True)
        
        # Manejar la carga de imágenes
        if 'imagenes' in request.files:
            files = request.files.getlist('imagenes')
            for file in files:
                if file and file.filename:
                    filename = file.filename
                    file.save(os.path.join(product_folder, filename))
        
        return redirect(url_for('index'))
    return render_template('add.html')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    conn = get_db()
    cursor = conn.cursor()
    if request.method == 'POST':
        descripcion = request.form['descripcion']
        stock = request.form['stock']
        cursor.execute('UPDATE producto SET descripcion = ?, stock = ? WHERE id = ?', (descripcion, stock, id))
        conn.commit()
        
        # Manejar la carga de imágenes
        if 'imagenes' in request.files:
            files = request.files.getlist('imagenes')
            product_folder = os.path.join(app.config['UPLOAD_FOLDER'], str(id))
            os.makedirs(product_folder, exist_ok=True)
            for file in files:
                if file and file.filename:
                    filename = file.filename
                    file.save(os.path.join(product_folder, filename))
        
        conn.close()
        return redirect(url_for('index'))
    cursor.execute('SELECT * FROM producto WHERE id = ?', (id,))
    producto = cursor.fetchone()
    conn.close()
    return render_template('edit.html', producto=producto)

@app.route('/delete/<int:id>')
def delete(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM producto WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    
    # Eliminar la carpeta del producto
    product_folder = os.path.join(app.config['UPLOAD_FOLDER'], str(id))
    if os.path.exists(product_folder):
        for file in os.listdir(product_folder):
            os.remove(os.path.join(product_folder, file))
        os.rmdir(product_folder)
    
    return redirect(url_for('index'))

@app.route('/uploads/<int:producto_id>/<filename>')
def uploaded_file(producto_id, filename):
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], str(producto_id)), filename)

@app.route('/product/<int:id>')
def product_detail(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM producto WHERE id = ?', (id,))
    producto = cursor.fetchone()
    
    if producto:
        # Obtener todas las imágenes si existen
        product_folder = os.path.join(app.config['UPLOAD_FOLDER'], str(id))
        if os.path.exists(product_folder):
            images = os.listdir(product_folder)
        else:
            images = []
    else:
        producto = {}
        images = []

    conn.close()
    return render_template('product_detail.html', producto=producto, images=images)

@app.route('/master')
def master():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM producto')
    productos = cursor.fetchall()
    conn.close()

    # Obtener la lista de imágenes para cada producto
    product_images = {}
    for producto in productos:
        product_folder = os.path.join(app.config['UPLOAD_FOLDER'], str(producto['id']))
        if os.path.exists(product_folder):
            images = os.listdir(product_folder)
            if images:
                product_images[producto['id']] = images[0]  # Solo la primera imagen
            else:
                product_images[producto['id']] = None

    return render_template('master.html', productos=productos, product_images=product_images)

if __name__ == '__main__':
    app.run(debug=True)
