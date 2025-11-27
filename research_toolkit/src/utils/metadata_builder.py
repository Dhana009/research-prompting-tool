# src/utils/metadata_builder.py

import datetime
import re
import uuid


class MetadataBuilder:

    @staticmethod
    def _now():
        return datetime.datetime.utcnow()

    @staticmethod
    def _short_id():
        # 5-character readable short id from uuid
        return uuid.uuid4().hex[:5].upper()

    @staticmethod
    def _timestamp_parts():
        now = MetadataBuilder._now()
        date = now.strftime("%Y%m%d")
        time = now.strftime("%H%M%S")
        return date, time

    @staticmethod
    def build(question, markdown_content="", parent_id=None, parent_conversation_id=None, tool_prefix="TR"):
        date, time = MetadataBuilder._timestamp_parts()
        short = MetadataBuilder._short_id()

        # --- 1. conversation_id ---
        if parent_conversation_id:
            conversation_id = parent_conversation_id
        else:
            conversation_id = f"CV-{date}-{time}-{short}"

        # --- 2. document_id (human readable) ---
        document_id = f"{tool_prefix}-{date}-{time}-{short}"

        # --- 3. parent_id ---
        pid = parent_id if parent_id else None

        # --- 4. content_type ---
        if MetadataBuilder._looks_like_code(markdown_content):
            content_type = "code"
        else:
            content_type = "text"

        return {
            "conversation_id": conversation_id,
            "document_id": document_id,
            "parent_id": pid,
            "content_type": content_type
        }

    @staticmethod
    def _looks_like_code(content):
        # simple heuristics for test expectations
        if re.search(r"\bdef\b|\breturn\b|{|\}|;", content):
            return True
        return False

