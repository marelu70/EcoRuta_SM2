from flask import Flask, render_template, request, redirect, url_for, session, flash
from bson import ObjectId
import bcrypt

# -------------------------------------------------------------
# IMPORTACIÓN DE LA CONEXIÓN DESDE TU ARCHIVO EXTERNO
# -------------------------------------------------------------
# Esto trae las variables limpias y evita que 'usuarios_col' quede indefinida
from conexionAtlas import usuarios_col, rutas_col, camiones_col, reportes_col, encuestas_col

app = Flask(__name__)
app.secret_key = "clave_secreta_super_segura_ecoruta_2026"


# -------------------------------------------------------------
# CREACIÓN DEL ADMINISTRADOR MAESTRO Y DATOS SEMILLA
# -------------------------------------------------------------
def verificar_o_crear_admin():
    try:
        # 1. Crear Administrador Maestro por defecto si no existe
        admin_existente = usuarios_col.find_one({"correo": "admin@ecoruta.gob.mx"})
        if not admin_existente:
            password_plana = "AdminEco2026!"
            password_encriptada = bcrypt.hashpw(password_plana.encode('utf-8'), bcrypt.gensalt())
            
            admin_default = {
                "usuario": "admin",
                "correo": "admin@ecoruta.gob.mx",
                "password": password_encriptada,
                "role": "admin"
            }
            usuarios_col.insert_one(admin_default)
            print("[EcoRuta] Administrador maestro creado con éxito.")
            
        # 2. Crear un usuario común de prueba (María García)
        user_existente = usuarios_col.find_one({"correo": "user@ecoruta.gob.mx"})
        if not user_existente:
            user_pass = bcrypt.hashpw("UserEco2026!".encode('utf-8'), bcrypt.gensalt())
            usuarios_col.insert_one({
                "usuario": "María García",
                "correo": "user@ecoruta.gob.mx",
                "password": user_pass,
                "role": "usuario"
            })
            print("[EcoRuta] Usuario de prueba (María García) creado.")

        # 3. Insertar datos simulados de Camiones si la colección está vacía
        if camiones_col.count_documents({}) == 0:
            camiones_col.insert_many([
                {
                    "placas": "TX-202",
                    "modelo": "Foton S12",
                    "capacidad": 5,
                    "chofer_responsable": "Jorge Samano",
                    "estado": "Óptimo",
                    "ultima_revision": "2026-02-15"
                },
                {
                    "placas": "MX-551",
                    "modelo": "International DuraStar",
                    "capacidad": 8,
                    "chofer_responsable": "Jose Eduardo Cruz",
                    "estado": "Mantenimiento",
                    "ultima_revision": "2026-04-10"
                }
            ])
            print("[EcoRuta] Datos semilla de camiones insertados.")

        # 4. Insertar datos simulados de Rutas
        if rutas_col.count_documents({}) == 0:
            rutas_col.insert_many([
                {
                    "nombre": "R001",
                    "zona": "Centro",
                    "horario": "08:00 AM - 10:00 AM",
                    "dias": "Lunes, Miércoles, Viernes",
                    "unidad_id": "TX-202",
                    "encuestas_satisfaccion": [
                        {
                            "fecha": "2026-04-20",
                            "puntuacion_limpieza": 5,
                            "puntuacion_puntualidad": 3,
                            "comentario": "Buena atención, pero a veces tardan."
                        },
                        {
                            "fecha": "2026-04-22",
                            "puntuacion_limpieza": 4,
                            "puntuacion_puntualidad": 4,
                            "comentario": "Todo bien hoy."
                        }
                    ]
                },
                {
                    "nombre": "R002",
                    "zona": "Barrio Guadalupe",
                    "horario": "10:30 AM - 01:30 PM",
                    "dias": "Martes, Jueves, Sábado",
                    "unidad_id": "MX-551",
                    "encuestas_satisfaccion": []
                }
            ])
            print("[EcoRuta] Datos semilla de rutas logísticas insertados.")

        # 5. Insertar datos simulados de Reportes Ciudadanos
        if reportes_col.count_documents({}) == 0:
            reportes_col.insert_one({
                "usuario": "María García",
                "ubicacion_incidente": "Calle Juárez #10",
                "asunto": "Omisión de ruta",
                "detalle": "El camión no pasó hoy a la hora de siempre.",
                "fecha_hora": "2026-03-12T08:30:00Z",
                "estado": "Pendiente"
            })
            print("[EcoRuta] Datos semilla de reportes ciudadanos insertados.")

        # 6. Insertar datos semilla en la colección independiente de encuestas
        if encuestas_col.count_documents({}) == 0:
            encuestas_col.insert_many([
                {
                    "usuario": "María García",
                    "id_ruta_evaluada": "R001",
                    "puntuacion_limpieza": 5,
                    "puntuacion_puntualidad": 3,
                    "comentarios": "Buena atención del personal, pero a veces tardan.",
                    "fecha_aplicacion": "2026-04-20"
                },
                {
                    "usuario": "Anónimo",
                    "id_ruta_evaluada": "R001",
                    "puntuacion_limpieza": 4,
                    "puntuacion_puntualidad": 4,
                    "comentarios": "Todo bien hoy.",
                    "fecha_aplicacion": "2026-04-22"
                }
            ])
            print("[EcoRuta] Datos semilla de encuestas de satisfacción insertados.")

    except Exception as e:
        print(f"[EcoRuta] Error al verificar o poblar la base de datos: {e}")

# Ejecutamos la función de datos semilla al arrancar
verificar_o_crear_admin()


# -------------------------------------------------------------
# RUTAS DE AUTENTICACIÓN Y LOGOUT
# -------------------------------------------------------------
@app.route('/')
def inicio():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash("Por favor rellena todos los campos.", "error")
            return redirect(url_for('login'))
            
        # Busca de forma directa en la colección importada desde conexionAtlas
        usuario = usuarios_col.find_one({
            "$or": [{"correo": username}, {"usuario": username}]
        })
        
        if usuario and bcrypt.checkpw(password.encode('utf-8'), usuario['password']):
            session['user'] = usuario['usuario']
            session['role'] = usuario['role']
            flash("¡Bienvenido al sistema!", "success")
            
            if usuario['role'] == 'admin':
                return redirect(url_for('dashboard_admin'))
            else:
                return redirect(url_for('dashboard_user'))
        else:
            flash("Credenciales incorrectas. Inténtalo de nuevo.", "error")
            return redirect(url_for('login'))
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("Sesión cerrada correctamente.", "info")
    return redirect(url_for('inicio'))


# -------------------------------------------------------------
# PANEL ADMINISTRADOR: CRUD COMPLETO + SEGUIMIENTO MUNICIPAL
# -------------------------------------------------------------
@app.route('/admin')
def dashboard_admin():
    if session.get('role') != 'admin':
        flash("Acceso denegado.", "error")
        return redirect(url_for('login'))
    
    lista_camiones = list(camiones_col.find())
    lista_rutas = list(rutas_col.find())
    lista_reportes = list(reportes_col.find())
    lista_encuestas = list(encuestas_col.find())
    
    return render_template('dashboard_admin.html', 
                           camiones=lista_camiones, 
                           rutas=lista_rutas, 
                           reportes=lista_reportes, 
                           encuestas=lista_encuestas)

# --- CRUD CAMIONES ---
@app.route('/admin/camion/agregar', methods=['POST'])
def agregar_camion():
    if session.get('role') != 'admin': return redirect(url_for('login'))
    camiones_col.insert_one({
        "placas": request.form.get('placas'),  
        "modelo": request.form.get('modelo'),
        "capacidad": float(request.form.get('capacidad', 0)),
        "chofer_responsable": request.form.get('chofer_responsable', "No asignado"),
        "estado": request.form.get('estado'),  
        "ultima_revision": request.form.get('ultima_revision', "2026-05-01")
    })
    flash("Camión agregado correctamente a Atlas.", "success")
    return redirect(url_for('dashboard_admin'))

@app.route('/admin/camion/editar/<id>', methods=['POST'])
def editar_camion(id):
    if session.get('role') != 'admin': return redirect(url_for('login'))
    camiones_col.update_one(
        {"_id": ObjectId(id)},
        {"$set": {
            "placas": request.form.get('placas'),
            "modelo": request.form.get('modelo'),
            "capacidad": float(request.form.get('capacidad', 0)),
            "chofer_responsable": request.form.get('chofer_responsable'),
            "estado": request.form.get('estado'),
            "ultima_revision": request.form.get('ultima_revision')
        }}
    )
    flash("Datos del camión actualizados.", "success")
    return redirect(url_for('dashboard_admin'))

@app.route('/admin/camion/eliminar/<id>')
def eliminar_camion(id):
    if session.get('role') != 'admin': return redirect(url_for('login'))
    camiones_col.delete_one({"_id": ObjectId(id)})
    flash("Camión eliminado de forma física de MongoDB Atlas.", "success")
    return redirect(url_for('dashboard_admin'))

# --- CRUD RUTAS ---
@app.route('/admin/ruta/agregar', methods=['POST'])
def agregar_ruta():
    if session.get('role') != 'admin': return redirect(url_for('login'))
    rutas_col.insert_one({
        "nombre": request.form.get('nombre'),  
        "zona": request.form.get('zona'),      
        "horario": request.form.get('horario'),
        "dias": request.form.get('dias').split(', '), 
        "unidad_id": request.form.get('unidad_id'),   
        "encuestas_satisfaccion": []                 
    })
    flash("Nueva ruta logística planificada.", "success")
    return redirect(url_for('dashboard_admin'))

@app.route('/admin/ruta/editar/<id>', methods=['POST'])
def editar_ruta(id):
    if session.get('role') != 'admin': return redirect(url_for('login'))
    rutas_col.update_one(
        {"_id": ObjectId(id)},
        {"$set": {
            "nombre": request.form.get('nombre'),
            "zona": request.form.get('zona'),
            "horario": request.form.get('horario'),
            "dias": request.form.get('dias').split(', '),
            "unidad_id": request.form.get('unidad_id')
        }}
    )
    flash("Ruta modificada con éxito.", "success")
    return redirect(url_for('dashboard_admin'))

@app.route('/admin/ruta/eliminar/<id>')
def eliminar_ruta(id):
    if session.get('role') != 'admin': return redirect(url_for('login'))
    rutas_col.delete_one({"_id": ObjectId(id)})
    flash("Ruta eliminado del itinerario municipal.", "success")
    return redirect(url_for('dashboard_admin'))

# --- CAMBIAR ESTADO DE REPORTE ---
@app.route('/admin/reporte/estado/<id>', methods=['POST'])
def cambiar_estado_reporte(id):
    if session.get('role') != 'admin': return redirect(url_for('login'))
    nuevo_estado = request.form.get('estado')  
    reportes_col.update_one(
        {"_id": ObjectId(id)},
        {"$set": {"estado": nuevo_estado}}
    )
    flash(f"El estatus del reporte cambió a: {nuevo_estado}", "success")
    return redirect(url_for('dashboard_admin'))


# -------------------------------------------------------------
# PANEL USUARIO: CONSULTAR DATOS + LEVANTAR REPORTES Y ENCUESTAS
# -------------------------------------------------------------
@app.route('/panel')
def dashboard_user():
    if not session.get('user'):
        flash("Por favor inicia sesión para acceder al panel ciudadano.", "error")
        return redirect(url_for('login'))
        
    lista_camiones = list(camiones_col.find())
    lista_rutas = list(rutas_col.find())
    mis_reportes = list(reportes_col.find({"usuario": session['user']}))
    
    return render_template('dashboard_user.html', 
                           camiones=lista_camiones, 
                           rutas=lista_rutas, 
                           reportes=mis_reportes)

# --- CREAR REPORTE ---
@app.route('/usuario/reporte/nuevo', methods=['POST'])
def crear_reporte():
    if not session.get('user'): return redirect(url_for('login'))
    reportes_col.insert_one({
        "usuario": session['user'],  
        "ubicacion_incidente": request.form.get('ubicacion_incidente'),
        "asunto": request.form.get('asunto'),  
        "detalle": request.form.get('detalle'), 
        "fecha_hora": "2026-05-21T16:22:00Z",
        "estado": "Pendiente"  
    })
    flash("Tu reporte de incidencia ha sido enviado a la delegación municipal.", "success")
    return redirect(url_for('dashboard_user'))

# --- CREAR ENCUESTA ---
@app.route('/usuario/encuesta/nueva', methods=['POST'])
def crear_encuesta():
    if not session.get('user'): return redirect(url_for('login'))
    
    id_ruta = request.form.get('id_ruta_evaluada')
    pnt_limpieza = int(request.form.get('puntuacion_limpieza', 5))
    pnt_puntualidad = int(request.form.get('puntuacion_puntualidad', 5))
    comentarios = request.form.get('comentarios')
    fecha_hoy = "2026-05-21"

    encuestas_col.insert_one({
        "usuario": session['user'],
        "id_ruta_evaluada": id_ruta,
        "puntuacion_limpieza": pnt_limpieza,
        "puntuacion_puntualidad": pnt_puntualidad,
        "comentarios": comentarios,
        "fecha_application": fecha_hoy
    })

    rutas_col.update_one(
        {"nombre": id_ruta},
        {"$push": {
            "encuestas_satisfaccion": {
                "fecha": fecha_hoy,
                "puntuacion_limpieza": pnt_limpieza,
                "puntuacion_puntualidad": pnt_puntualidad,
                "comentario": comentarios
            }
        }}
    )
    
    flash("Encuesta de satisfacción registrada correctamente.", "success")
    return redirect(url_for('dashboard_user'))


if __name__ == '__main__':
    app.run(debug=True)