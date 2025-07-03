import os

import pytest

HOST_ADDRESS = os.getenv("HOST_ADDRESS", "http://127.0.0.1:9380")
VERSION = "v1"
ZHIPU_AI_API_KEY = os.getenv("ZHIPU_AI_API_KEY")
if ZHIPU_AI_API_KEY is None:
    pytest.exit("Error: Environment variable ZHIPU_AI_API_KEY must be set")

EMAIL = "qa@infiniflow.org"
# password is "123"
PASSWORD = """ctAseGvejiaSWWZ88T/m4FQVOpQyUvP+x7sXtdv3feqZACiQleuewkUi35E16wSd5C5QcnkkcV9cYc8TKPTRZlxappDuirxghxoOvFcJxFU4ixLsD
fN33jCHRoDUW81IH9zjij/vaw8IbVyb6vuwg6MX6inOEBRRzVbRYxXOu1wkWY6SsI8X70oF9aeLFp/PzQpjoe/YbSqpTq8qqrmHzn9vO+yvyYyvmDsphXe
X8f7fp9c7vUsfOCkM+gHY3PadG+QHa7KI7mzTKgUTZImK6BZtfRBATDTthEUbbaTewY4H0MnWiCeeDhcbeQao6cFy1To8pE3RpmxnGnS8BsBn8w=="""

INVALID_API_TOKEN = "invalid_key_123"
DATASET_NAME_LIMIT = 128
DOCUMENT_NAME_LIMIT = 255
CHAT_ASSISTANT_NAME_LIMIT = 255
SESSION_WITH_CHAT_NAME_LIMIT = 255
