import pytest
import pandas as pd
import datetime
from migrate import transform_data, insert_data, get_mongo_client   

@pytest.fixture
def healthcare_data():
    """
    Fixture qui charge et transforme le dataset CSV.
    Utilisée par les tests de transformation des données.
    """
    df = pd.read_csv('data/healthcare_dataset.csv')
    return transform_data(df)

@pytest.fixture(scope="module")
def mongo_client():
    """
    Fixture partagée entre tous les tests du module.
    Crée une connexion MongoDB et nettoie la collection de test après les tests.
    scope="module" permet de réutiliser la même connexion pour tous les tests MongoDB.
    """
    client = get_mongo_client()
    yield client
    client["test_healthcare"].drop_collection("patients_records")
    client.close()


def test_columns_name(healthcare_data):
    """Vérifie que les colonnes sont bien renommées en snake_case après transformation."""
    expected_columns = [
        'name', 'age', 'gender', 'blood_type', 'medical_condition',
        'date_of_admission', 'doctor', 'hospital', 'insurance_provider',
        'billing_amount', 'room_number', 'admission_type', 'discharge_date',
        'medication', 'test_results'
       ]
    assert list(healthcare_data.columns) == expected_columns

def test_columns_type(healthcare_data):
    """Vérifie que les types des colonnes sont correctement convertis."""
    assert str(healthcare_data["age"].dtype).startswith("int")
    assert str(healthcare_data["room_number"].dtype).startswith("int")
    assert str(healthcare_data["billing_amount"].dtype).startswith("float")
    assert str(healthcare_data["date_of_admission"].dtype).startswith("datetime64")
    assert str(healthcare_data["discharge_date"].dtype).startswith("datetime64")

def test_row_count(healthcare_data):
    """Vérifie qu'aucune ligne n'est perdue lors de la transformation (hors doublons)."""
    df = pd.read_csv('data/healthcare_dataset.csv').drop_duplicates()
    assert len(healthcare_data) == len(df)

def test_null_values(healthcare_data):
    """Vérifie l'absence de valeurs nulles dans le DataFrame transformé."""
    assert healthcare_data.isnull().sum().sum() == 0

def test_duplicated_values(healthcare_data):
    """Vérifie l'absence de doublons dans le DataFrame transformé."""
    assert healthcare_data.duplicated().sum() == 0

def test_insert_data(healthcare_data, mongo_client):
    """
    Vérifie que le nombre de documents insérés dans MongoDB
    correspond au nombre de lignes du DataFrame.
    """
    insert_data(df=healthcare_data, db_name="test_healthcare", client=mongo_client)
    db = mongo_client["test_healthcare"]
    collection = db["patients_records"]
    assert collection.count_documents({}) == len(healthcare_data)

def test_mongodb_field_types(mongo_client):
    """
    Vérifie que les types des champs stockés dans MongoDB
    correspondent aux types attendus.
    """
    db = mongo_client["test_healthcare"]
    collection = db["patients_records"]
    record = collection.find_one()
    assert isinstance(record["age"], int)
    assert isinstance(record["room_number"], int)
    assert isinstance(record["billing_amount"], float)
    assert isinstance(record["date_of_admission"], datetime.datetime)
    assert isinstance(record["discharge_date"], datetime.datetime)

