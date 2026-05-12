from pymongo  import MongoClient
import os


def get_admin_client():
    """
    Crée et retourne une connexion MongoDB avec les credentials root.
    Utilise les variables d'environnement 
    MONGO_INITDB_ROOT_USERNAME et MONGO_INITDB_ROOT_PASSWORD pour l'authentification.
    """
    root_username = os.getenv("MONGO_INITDB_ROOT_USERNAME")
    root_password = os.getenv("MONGO_INITDB_ROOT_PASSWORD")
    host = os.getenv("MONGO_HOST", "localhost")
    return MongoClient(f"mongodb://{root_username}:{root_password}@{host}:27017/")

def create_users(client=None):
    """
    Crée les utilisateurs MongoDB avec leurs rôles respectifs :
    - app_user : lecture/écriture sur healthcare et test_healthcare
    - reader_user : lecture seule sur healthcare et test_healthcare
    Les credentials sont récupérés depuis les variables d'environnement.
    """
    app_user = os.getenv("MONGO_APP_USER")
    app_password = os.getenv("MONGO_APP_PASSWORD")
    reader_user = os.getenv("MONGO_READER_USER")
    reader_password = os.getenv("MONGO_READER_PASSWORD")
    database = os.getenv("MONGO_INITDB_DATABASE")

    if client is None:
        client = get_admin_client()

    db = client["admin"]

    # Création de l'utilisateur applicatif avec droits lecture/écriture
    db.command("createUser", app_user,
               pwd = app_password,
               roles=[{"role": "readWrite", "db" : database},
                      {"role": "readWrite", "db": f"test_{database}"}]
    )
    # Création de l'utilisateur en lecture seule
    db.command("createUser", reader_user,
               pwd = reader_password,
               roles=[{"role": "read", "db" : database},
                      {"role": "read", "db": f"test_{database}"}]
    )

if __name__ == "__main__" :
    create_users()