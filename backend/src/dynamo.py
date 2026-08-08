# Raw session logging
## DynamoDB stores raw chat turns for later analysis, such as auditing or debugging. 
## This is a simple, low-level logging mechanism that doesn't do any filtering or summarization 
## It just records the raw question/answer pairs along with some metadata (session ID, user ID, timestamp).
import os
import time
import uuid

import boto3

TABLE_NAME = os.getenv("DYNAMO_TABLE", "timess-sessions")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

_table = None


def get_table():
    global _table
    if _table is None:
        dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
        _table = dynamodb.Table(TABLE_NAME)
    return _table


def log_turn(session_id: str, user_id: str, question: str, answer: str) -> None:
    """
    Writes one item per chat turn. Wrapped in try/except on purpose:
    logging should never be able to break an actual chat response --
    e.g. during local dev without AWS credentials configured, the
    bot should keep working, just without this side effect.
    """
    try:
        table = get_table()
        table.put_item(
            Item={
                "session_id": session_id,
                "turn_id": str(uuid.uuid4()),
                "user_id": user_id,
                "timestamp": int(time.time()),
                "question": question,
                "answer": answer,
            }
        )
    except Exception:
        pass