import os
from enum import Enum
from dataclasses import dataclass, fields, field
from typing import Any, Optional, Dict 
from pydantic import Field


@dataclass(kw_only=True)
class Configuration:
    """The configurable fields for semantic similarity processing."""

    # Models
    embeddings_model: str = "text-embedding-3-large"
