

from enum import Enum

# noqa  MC8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2TWxOU1ZnPT06YmUxNzFkNDY=

class DocStatus(str, Enum):
    """Document processing status"""
# pragma: no cover  MS8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2TWxOU1ZnPT06YmUxNzFkNDY=

    READY = "ready"
    HANDLING = "handling"
    PENDING = "pending"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"
