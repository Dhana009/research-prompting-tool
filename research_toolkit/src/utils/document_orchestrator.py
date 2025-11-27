# src/utils/document_orchestrator.py

from .metadata_builder import MetadataBuilder
from .document_assembler import DocumentAssembler
from .mongo_writer import MongoWriter


class DocumentOrchestrator:

    @staticmethod
    def save_document(
        question,
        markdown_content,
        mongo_client,
        database_name,
        collection_name,
        parent_id=None,
        additional_fields=None,
        tool_prefix="TR"
    ):
        """
        Full System-1 pipeline:
        - load parent
        - build metadata
        - assemble document
        - save to Mongo
        
        Args:
            question: Research question
            markdown_content: Markdown response content
            mongo_client: MongoDB client instance
            database_name: Database name
            collection_name: Collection name
            parent_id: Optional parent document ID
            additional_fields: Optional dict of additional fields to include in document
            tool_prefix: Tool prefix for document_id (TR, CR, DB, AR, GP)
        """

        parent_doc = None

        # --- Load parent if provided ---
        if parent_id:
            parent_doc = DocumentOrchestrator._load_parent(
                mongo_client, database_name, collection_name, parent_id
            )
            if parent_doc is None:
                raise ValueError("parent document not found")

        # --- Assemble full document ---
        full_doc = DocumentAssembler.build(
            question=question,
            markdown_content=markdown_content,
            parent=parent_doc,
            additional_fields=additional_fields,
            tool_prefix=tool_prefix
        )

        # --- Save into Mongo ---
        result = MongoWriter.save(
            doc=full_doc,
            mongo_client=mongo_client,
            database_name=database_name,
            collection_name=collection_name
        )

        return result

    @staticmethod
    def _load_parent(mongo_client, database_name, collection_name, parent_id):
        """
        Loads a parent document from MongoDB.
        Searches by both document_id and question_id for backward compatibility.
        """
        if database_name not in mongo_client.list_database_names():
            raise ValueError(f"Database '{database_name}' does not exist")

        db = mongo_client[database_name]

        if collection_name not in db.list_collection_names():
            raise ValueError(f"Collection '{collection_name}' does not exist")

        collection = db[collection_name]

        # Try document_id first (new format), then question_id (old format)
        doc = collection.find_one({"document_id": parent_id})
        if doc is None:
            doc = collection.find_one({"question_id": parent_id})
        
        return doc

