from pymongo import MongoClient

# Tu URI de conexión a MongoDB Atlas
MONGO_URI = "mongodb+srv://ks1398501_db_user:4JD5JcLp75fgafTA@cluster0.j78ycv4.mongodb.net/?appName=Cluster0"

try:
    client = MongoClient(MONGO_URI, tls=True, tlsAllowInvalidCertificates=True)
    db = client['EcoRuta']
    print("[EcoRuta] Conexión exitosa a MongoDB Atlas.")
except Exception as e:
    print(f"[EcoRuta] Error al conectar: {e}")

# Variables de las colecciones totalmente alineadas a la izquierda
usuarios_col = db['usuarios']
rutas_col = db['rutas']
camiones_col = db['camiones']
reportes_col = db['reportes']
encuestas_col = db['encuestas']
