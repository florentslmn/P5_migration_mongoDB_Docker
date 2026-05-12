import pytest
import pandas as pd
import datetime
from migrate import transform_data, insert_data, get_mongo_client   

@pytest.fixture
def healthcare_data():
    df = pd.read_csv('data/healthcare_dataset.csv')
    return transform_data(df)

@pytest.fixture(scope="module")
def mongo_client():
    client = get_mongo_client()
    yield client
    client["test_healthcare"].drop_collection("patients_records")
    client.close()


def test_columns_name(healthcare_data):
    expected_columns = [
        'name', 'age', 'gender', 'blood_type', 'medical_condition',
        'date_of_admission', 'doctor', 'hospital', 'insurance_provider',
        'billing_amount', 'room_number', 'admission_type', 'discharge_date',
        'medication', 'test_results'
       ]
    assert list(healthcare_data.columns) == expected_columns

def test_columns_type(healthcare_data):
    assert str(healthcare_data["age"].dtype).startswith("int")
    assert str(healthcare_data["room_number"].dtype).startswith("int")
    assert str(healthcare_data["billing_amount"].dtype).startswith("float")
    assert str(healthcare_data["date_of_admission"].dtype).startswith("datetime64")
    assert str(healthcare_data["discharge_date"].dtype).startswith("datetime64")

def test_row_count(healthcare_data):
    df = pd.read_csv('data/healthcare_dataset.csv').drop_duplicates()
    assert len(healthcare_data) == len(df)

def test_null_values(healthcare_data):
    assert healthcare_data.isnull().sum().sum() == 0

def test_duplicated_values(healthcare_data):
    assert healthcare_data.duplicated().sum() == 0

def test_insert_data(healthcare_data, mongo_client):

    insert_data(df=healthcare_data, db_name="test_healthcare", client=mongo_client)
    db = mongo_client["test_healthcare"]
    collection = db["patients_records"]
    assert collection.count_documents({}) == len(healthcare_data)

def test_mongodb_field_types(mongo_client):
    db = mongo_client["test_healthcare"]
    collection = db["patients_records"]
    record = collection.find_one()
    assert isinstance(record["age"], int)
    assert isinstance(record["room_number"], int)
    assert isinstance(record["billing_amount"], float)
    assert isinstance(record["date_of_admission"], datetime.datetime)
    assert isinstance(record["discharge_date"], datetime.datetime)

