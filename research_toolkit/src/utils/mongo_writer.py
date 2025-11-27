# src/utils/mongo_writer.py

from pymongo.errors import DuplicateKeyError


class MongoWriter:

    @staticmethod
    def save(doc, mongo_client, database_name, collection_name):
        """
        Saves a System-1 document into MongoDB with validation and duplicate protection.
        """

        # --- Validate DB exists ---
        if database_name not in mongo_client.list_database_names():
            raise ValueError(f"DB not found: '{database_name}'")

        db = mongo_client[database_name]

        # --- Validate collection exists ---
        if collection_name not in db.list_collection_names():
            raise ValueError(f"collection not found: '{collection_name}'")

        collection = db[collection_name]

        # --- Prevent duplicate document_id ---
        existing = collection.find_one({"document_id": doc["document_id"]})
        if existing:
            raise ValueError(f"duplicate document_id: {doc['document_id']}")

        # --- Insert document ---
        result = collection.insert_one(doc)

        # --- Clean output ---
        return {
            "document_id": doc["document_id"],
            "conversation_id": doc["conversation_id"],
            "parent_id": doc["parent_id"],
            "content_type": doc["content_type"],
            "mongo_db": database_name,
            "mongo_collection": collection_name,
            "inserted_id": str(result.inserted_id),
        }

