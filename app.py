from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)

DATABASE = 'propiedades.db'

# Crear base de datos si no existe
def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS propiedades (
            Orden INTEGER PRIMARY KEY,
            Producto TEXT,
            Precio DECIMAL(10, 2),
            Ciudad TEXT,
            URL VARCHAR(255),
            Fecha DATE,
            Interes_count INTEGER DEFAULT 0
        )
    ''')
    conn.commit()

    # Verificar si hay datos, si no importar desde CSV
    c.execute('SELECT COUNT(*) FROM propiedades')
    if c.fetchone()[0] == 0:
        df = pd.read_csv('datos_prop/propiedades.csv')
        for _, row in df.iterrows():
            print(row)
            orden = int(row['Orden'])
            producto = str(row['Producto'])
            precio = float(row['Precio'])
            ciudad = str(row['Ciudad'])
            url = str(row['URL'])
            fecha = pd.to_datetime(row['Fecha']).date().isoformat()  # 'YYYY-MM-DD'

            c.execute('''
                INSERT INTO propiedades (Orden, Producto, Precio, Ciudad, URL, Fecha)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (orden, producto, precio, ciudad, url, fecha))

        conn.commit()

    conn.close()

@app.route('/')
def index():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT * FROM propiedades ORDER BY Orden')
    propiedades = c.fetchall()
    conn.close()
    return render_template('index.html', propiedades=propiedades)

@app.route('/me_gusta/<int:orden>', methods=['POST'])
def me_gusta(orden):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('UPDATE propiedades SET Interes_count = Interes_count + 1 WHERE Orden = ?', (orden,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
