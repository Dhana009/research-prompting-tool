# src/utils/document_assembler.py

from .metadata_builder import MetadataBuilder


class DocumentAssembler:

    @staticmethod
    def build(question, markdown_content, parent=None, additional_fields=None, tool_prefix="TR"):
        """
        Builds a full document ready to be inserted into MongoDB.
        
        Args:
            question: Research question
            markdown_content: Markdown response content
            parent: Optional parent document dict
            additional_fields: Optional dict of additional fields to include
            tool_prefix: Tool prefix for document_id (TR, CR, DB, AR, GP)
        """

        # Extract parent fields if parent exists
        parent_id = None
        parent_conversation_id = None

        if parent:
            parent_id = parent.get("document_id") or parent.get("question_id")
            parent_conversation_id = parent.get("conversation_id")

        # Generate metadata using MetadataBuilder
        metadata = MetadataBuilder.build(
            question=question,
            markdown_content=markdown_content,
            parent_id=parent_id,
            parent_conversation_id=parent_conversation_id,
            tool_prefix=tool_prefix
        )

        # Assemble final document for MongoDB
        assembled = {
            "conversation_id": metadata["conversation_id"],
            "document_id": metadata["document_id"],
            "parent_id": metadata["parent_id"],
            "content_type": metadata["content_type"],
            "question": question,
            "markdown_content": markdown_content,
        }
        
        # Merge additional fields if provided (for backward compatibility with old schema)
        if additional_fields:
            assembled.update(additional_fields)

        return assembled

