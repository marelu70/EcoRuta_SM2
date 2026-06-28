from pymongo import MongoClient

# Tu URI de conexión a MongoDB Atlas
MONGO_URI = "mongodb+srv://ks1398501_db_user:4JD5JcLp75fgafTA@cluster0.j78ycv4.mongodb.net/?appName=Cluster0"

try:
    # Ajustamos los parámetros al nuevo estándar moderno de PyMongo
   client = MongoClient(MONGO_URI, tls=True, tlsAllowInvalidCertificates=True)
        MONGO_URI,
        tls=True,
        tlsAllowInvalidCertificates=True  # Parche definitivo moderno para el bloqueo del internet escolar
    )
    db = client['EcoRuta']
    
    # Declaramos las colecciones fijas
    usuarios_col = db['usuarios']
    rutas_col = db['rutas']
    camiones_col = db['camiones']
    reportes_col = db['reportes_ciudadanos']
    encuestas_col = db['encuestas_de_satisfaccion']
    
    print("[EcoRuta] Conexión exitosa a MongoDB Atlas desde conexionAtlas.py.")
except Exception as e:
    print(f"[EcoRuta] Error crítico de conexión en conexionAtlas.py: {e}")
