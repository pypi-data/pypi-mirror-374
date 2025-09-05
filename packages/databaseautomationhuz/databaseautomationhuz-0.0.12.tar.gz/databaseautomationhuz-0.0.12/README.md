# databseautomationhuz

This is a lightweight Python package that simplifies working with MongoDB. It provides an easy-to-use interface for creating clients, connecting to databases, managing collections, inserting single or multiple records, and performing bulk inserts directly from CSV or Excel files. With built-in type safety checks and automatic handling of database/collection creation, it reduces boilerplate code and prevents common errors when interacting with MongoDB. Ideal for data engineering, ETL pipelines, and machine learning projects that require structured data storage and quick dataset imports into MongoDB.

## Example Usage

```python
# !pip install databaseautomationhuz
from databaseautomationhuz.mongo_crud import MongoOperation

# Step 1: Initialize the MongoOperation object
mongo = MongoOperation(
    client_url="mongodb+srv://huzaifaahmedzaidi:@cluster0.yipsi0i.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0",
    database_name="firstmongodbconnection"
)

# Step 2: Create collection
collection = mongo.create_collection("my_collection2")

# Step 3: Insert a single record
mongo.insert_record(
    record={"name": "Huzaifa", "age": 24, "role": "ML Engineer"},
    collection_name="my_collection2"
)

# Step 4: Insert multiple records
mongo.insert_record(
    record=[
        {"name": "Ali", "age": 25, "role": "Data Scientist"},
        {"name": "Sara", "age": 22, "role": "Developer"}
    ],
    collection_name="my_collection2"
)

# Step 5: Bulk insert from CSV (students.csv should be in same folder)
# mongo.bulk_insert("students.csv", "my_collection2")

print("All data inserted successfully!")

