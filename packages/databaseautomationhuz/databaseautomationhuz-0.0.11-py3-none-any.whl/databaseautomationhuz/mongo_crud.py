from typing import Optional
import pandas as pd
from pymongo.mongo_client import MongoClient
import json


class MongoOperation:
    def __init__(self, client_url: str, database_name: str, collection_name: Optional[str] = None):
        self.client_url = client_url
        self.database_name = database_name
        self.collection_name = collection_name
        self._client = None
        self._database = None
        self._collection = None

    def create_mongo_client(self):
        if self._client is None:
            self._client = MongoClient(self.client_url)
        return self._client

    def create_database(self):
        if self._database is None:
            client = self.create_mongo_client()
            self._database = client[self.database_name]
        return self._database

    def create_collection(self, collection_name: Optional[str] = None):
        if collection_name:
            self.collection_name = collection_name

        if not self.collection_name:
            raise ValueError("Collection name must be provided.")

        if self._collection is None or self._collection.name != self.collection_name:
            database = self.create_database()
            self._collection = database[self.collection_name]

        return self._collection

    def insert_record(self, record, collection_name: str):
        """Insert a single record (dict) or multiple records (list of dicts)."""
        if type(record) == list:
            for data in record:
                if type(data) != dict:
                    raise TypeError("Each record must be a dict")
            collection = self.create_collection(collection_name)
            result = collection.insert_many(record)
            return f"{len(result.inserted_ids)} documents inserted"

        elif type(record) == dict:
            collection = self.create_collection(collection_name)
            result = collection.insert_one(record)
            return f"1 document inserted with id {result.inserted_id}"

        else:
            raise TypeError("record must be a dict or list of dicts")

    def bulk_insert(self, datafile: str, collection_name: Optional[str] = None):
        """Insert records from CSV or Excel into MongoDB."""
        if datafile.endswith('.csv'):
            dataframe = pd.read_csv(datafile, encoding='utf-8')
        elif datafile.endswith(".xlsx"):
            dataframe = pd.read_excel(datafile)
        else:
            raise ValueError("Unsupported file format. Use CSV or XLSX.")

        datajson = json.loads(dataframe.to_json(orient='records'))
        collection = self.create_collection(collection_name)
        result = collection.insert_many(datajson)
        return f"{len(result.inserted_ids)} records inserted successfully into '{collection.name}'"
