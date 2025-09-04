import os
from enum import Enum
from dataclasses import dataclass, fields, field
from typing import Any, Optional, Dict 


@dataclass(kw_only=True)
class Configuration:
    """The configurable fields for the MCP layer."""
    # Vector Store Indexes
    vector_store_groups_name: str = "faiss_index_groups"
    vector_store_tools_name: str = "faiss_index_tools"

    # number of K results to return
    number_of_relevant_groups: int = 3
    threshold_for_relevant_groups: float = 0.2
    number_of_filtered_groups: int = 2

    number_of_relevant_tools: int = 25

    # LLM model
    llm_model: str = "gpt-4o-mini"
    
    # Models
    embeddings_model: str = "text-embedding-3-large"
    
    # External API keys (can be provided via args or environment)
    coingecko_api_key: Optional[str] = None
    fred_api_key: Optional[str] = None

    # Populated after initialization
    mcps: list[dict[str, Any]] = field(init=False, repr=False)

    def __post_init__(self):
        # Default from environment if not provided
        if self.coingecko_api_key is None:
            self.coingecko_api_key = os.getenv("COINGECKO_PRO_API_KEY")
        if self.fred_api_key is None:
            self.fred_api_key = os.getenv("FRED_API_KEY")

        # Build MCP configuration dynamically so it can use instance values
        self.mcps = [
            {
                "group_name": "math",
                "group_description": "MCPs for performing math operations.",
                "mcps": [
                    {
                        "name": "math",
                        "description": "MCP Server for Math Operations.",
                        "mcp_config": {
                            "command": "python",
                            "args": ["-m", "mcp_layer.mcp_server.math_server"],
                            "transport": "stdio",
                        }
                    }
                ]
            },
            {
                "group_name": "coingecko",
                "group_description": "MCP Server for Crypto Price & Market Data using Coingecko data.",
                "mcps": [
                    {
                        "name": "coingecko",
                        "description": "MCP Server for Crypto Price & Market Data extracted from Coingecko.",
                        "mcp_config": {
                            "command": "npx",
                            "args": [
                                "-y",
                                "@coingecko/coingecko-mcp"
                            ],
                            "transport": "stdio",
                            "env": {
                                "COINGECKO_PRO_API_KEY": self.coingecko_api_key,
                                "COINGECKO_ENVIRONMENT": "pro"
                            }
                        }
                    }
                ]
            },
            {
                "group_name": "fred",
                "group_description": "MCP Server for Economic Data extracted from FRED.",
                "mcps": [
                    {
                        "name": "fred",
                        "description": "MCP Server for Economic Data extracted from FRED.",
                        "mcp_config": {
                            "command": "npx",
                            "args": [
                                "-y",
                                "@smithery/cli@latest",
                                "run",
                                "@stefanoamorelli/fred-mcp-server",
                                "--key",
                                (self.fred_api_key),
                                "--profile",
                                "basic-chameleon-Tg0vP1"
                            ],
                            "transport": "stdio"
                        }
                    }
                ]
            },
            {
                "group_name": "defillama",
                "group_description": "MCP Server for Crypto TVL data extracted from Defillama.",
                "mcps": [
                    {
                        "name": "defillama",
                        "description": "MCP Server for Crypto TVL data extracted from Defillama.",
                        "mcp_config": {
                            "command": "python",
                            "args": ["-m", "mcp_layer.mcp_server.llama_server"],
                            "transport": "stdio",
                        }
                    }
                ]
            }
        ]