from typing import Union, List, Dict
import pandas as pd
from pymongo.mongo_client import MongoClient
import json
from ensure import ensure_annotations


class MongoOperation:
    def __init__(self, client_url: str, database_name: str, collection_name: str = None):
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

    def create_collection(self, collection_name: str = None):
        if collection_name:
            self.collection_name = collection_name

        if not self.collection_name:
            raise ValueError("Collection name must be provided.")

        if self._collection is None or self._collection.name != self.collection_name:
            database = self.create_database()
            self._collection = database[self.collection_name]

        return self._collection

    @ensure_annotations
    def insert_record(self, record: Union[Dict, List[Dict]], collection_name: str):
        if isinstance(record, list):
            for data in record:
                if not isinstance(data, dict):
                    raise TypeError("Each record must be a dict")
            collection = self.create_collection(collection_name)
            collection.insert_many(record)
            return f"{len(record)} documents inserted"
    
        elif isinstance(record, dict):
            collection = self.create_collection(collection_name)
            collection.insert_one(record)
            return "1 document inserted"


    def bulk_insert(self, datafile: str, collection_name: str = None):
        if datafile.endswith('.csv'):
            dataframe = pd.read_csv(datafile, encoding='utf-8')
        elif datafile.endswith(".xlsx"):
            dataframe = pd.read_excel(datafile)
        else:
            raise ValueError("Unsupported file format. Use CSV or XLSX.")

        datajson = json.loads(dataframe.to_json(orient='records'))
        collection = self.create_collection(collection_name)
        collection.insert_many(datajson)
        return f"{len(datajson)} records inserted successfully into '{collection.name}'"
