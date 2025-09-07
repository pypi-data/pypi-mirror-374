from typing import Any, Optional, Union, List, Dict
import pandas as pd
from pymongo.mongo_client import MongoClient
import json


class MongoOperation:
    __collection = None  
    __database = None
    
    def __init__(self, client_url: str, database_name: str, collection_name: Optional[str] = None):
        self.client_url = client_url
        self.database_name = database_name
        self.collection_name = collection_name
       
    def create_mongo_client(self, collection: Optional[str] = None):
        client: MongoClient = MongoClient(self.client_url)
        return client
    
    def create_database(self, collection: Optional[str] = None):
        if MongoOperation.__database is None:
            client = self.create_mongo_client(collection)
            self.database = client[self.database_name]
            MongoOperation.__database = self.database
        return self.database 
    
    def create_collection(self, collection: Optional[str] = None):
        if MongoOperation.__collection is None:
            database = self.create_database(collection)
            self.collection = database[self.collection_name]
            MongoOperation.__collection = collection
        
        if MongoOperation.__collection != collection:
            database = self.create_database(collection)
            self.collection = database[self.collection_name]
            MongoOperation.__collection = collection
            
        return self.collection
    
    def insert_record(self, record: Union[Dict, List[Dict]], collection_name: str) -> Any:
        if isinstance(record, list):
            for data in record:
                if not isinstance(data, dict):
                    raise TypeError("Each record must be a dict")    
            collection = self.create_collection(collection_name)
            collection.insert_many(record)
        elif isinstance(record, dict):
            collection = self.create_collection(collection_name)
            collection.insert_one(record)
    
    def bulk_insert(self, datafile: str, collection_name: Optional[str] = None):
        self.path = datafile
        
        if self.path.endswith('.csv'):
            dataframe = pd.read_csv(self.path, encoding='utf-8')
            
        elif self.path.endswith(".xlsx"):
            dataframe = pd.read_excel(self.path)  # encoding not needed
            
        else:
            raise ValueError("Unsupported file format. Use .csv or .xlsx")
        
        datajson = json.loads(dataframe.to_json(orient='records'))
        collection = self.create_collection(collection_name)
        collection.insert_many(datajson)
    
    def read_records(self, collection_name: str) -> List[Dict]:
        collection = self.create_collection(collection_name)
        if collection is None:
            raise ValueError(f"Collection {collection_name} not found")

        return list(collection.find())
    
    def read_record(self, collection_name: str, record_id: str) -> Dict:
        collection = self.create_collection(collection_name)
        if collection is None:
            raise ValueError(f"Collection {collection_name} not found")
        
        return collection.find_one({"_id": record_id})
