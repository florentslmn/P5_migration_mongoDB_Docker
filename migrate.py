import pandas as pd
from pymongo  import MongoClient
import os

def get_mongo_client():
    """
    Crée et retourne une connexion MongoDB.
    Utilise MONGODB_URI si définie (Docker), sinon se connecte en local via MONGO_HOST.
    """
    uri = os.getenv("MONGODB_URI")
    if uri:
        return MongoClient(uri)
    host = os.getenv("MONGO_HOST", "localhost")
    return MongoClient(f"mongodb://{host}:27017/")

def transform_data(df):
    """
    Transforme le DataFrame brut issu du CSV :
    - Supprime les doublons
    - Convertit les types des colonnes (int, float, datetime)
    - Renomme les colonnes en snake_case minuscules
    """

    df = df.drop_duplicates()

    # Conversion des types numériques
    df = df.astype({
        "Age": "int",
        "Room Number": "int",
        "Billing Amount": "float"
    })
    # Conversion des colonnes de dates en datetime
    df["Date of Admission"] = pd.to_datetime(df["Date of Admission"])
    df["Discharge Date"] = pd.to_datetime(df["Discharge Date"])

    # Renommage des colonnes en snake_case pour MongoDB
    df.columns = [col.lower().replace(" ", "_") for col in df.columns]

    return df

def insert_data(df, db_name, client=None):
    """
    Insère les données transformées dans la collection MongoDB 'patients_records'.
    Vide la collection avant l'insertion pour éviter les doublons.
    Crée des index sur 'name' et 'date_of_admission' pour optimiser les requêtes.
    """
    if client is None:
        client = get_mongo_client()
    db = client[db_name]
    collection = db["patients_records"]

    # Conversion du DataFrame en liste de dictionnaires pour MongoDB
    data = df.to_dict("records")

    # Vidage de la collection avant insertion
    collection.delete_many({})
    if data: 
        collection.insert_many(data)

    # Création des index
    collection.create_index("name")
    collection.create_index("date_of_admission")

def export_data(db_name, client=None):
    """
    Exporte l'ensemble des documents de la collection MongoDB vers un fichier CSV
    dans le dossier output/.
    """
    if client is None:
        client = get_mongo_client()

    db = client[db_name]
    collection = db["patients_records"]

    # Récupération de tous les documents
    cursor = collection.find({})
    data = list(cursor)

    # Export vers CSV
    df_export = pd.DataFrame(data)
    df_export.to_csv("output/export_healthcare.csv", index=False)


if __name__ == "__main__" :
    df = pd.read_csv('data/healthcare_dataset.csv')
    df = transform_data(df)
    insert_data(df,"healthcare")
    export_data("healthcare")
