from mcp.server.fastmcp import FastMCP
import requests
import json
from typing import Dict, List, Union
from penelopedefillama import LlamaService


mcp = FastMCP("Llama")

'''
class LlamaService:
    BASE_URL = "https://api.llama.fi"
    BASE_URL_V2 = "https://api.llama.fi/v2"
    
    def __init__(self):
        # Lists of chains and protocols of interest
        self.coins_chains = [
            "bitcoin", "ethereum", "cosmos", "polkadot", "cardano", "solana", "avalanche-2", "near", "fantom", "kaspa",
            "matic-network", "arbitrum", "optimism", "band-protocol", "stellar", "algorand", "ripple", "dydx", "aave"
        ]
        self.coins_protocol = [
            "lido", "rocket-pool", "frax-swap", "quantumx-network", "linkswap", "api3", "velodrome", "gmx-v1",
            "uniswap", "sushiswap", "pancakeswap", "pendle", "1inch-network", "ocean-one"
        ]
        # Initialize a session for making requests
        self.session = requests.Session()

    def get_llama_chains(self) -> List[Dict]:
        """
        Retrieves blockchains data from the DefiLlama API and filters it based on predefined `coins_chains` of interest.

        Returns:
            List[Dict]: A list of dictionaries for each chain, where each dictionary contains:
                - 'coin': The name of the blockchain.
                - 'tvl': The formatted total value locked (TVL) for the blockchain.
                - 'type': A string indicating the data type, set to 'chain'.
        """
        url = 'https://api.llama.fi/chains'
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                filtered_data = []

                # Filter the chains data by the coins of interest
                
                for chain in data:
                    if chain['gecko_id'] in self.coins_chains or chain['name'].lower().replace(" ", "-") in [coin.lower() for coin in self.coins_chains]:
                        formatted_tvl = self.format_number_short(chain['tvl']) if 'tvl' in chain else '0'
                        
                        filtered_data.append({
                            'coin': chain['name'],
                            'tvl': formatted_tvl,
                            'type': 'chain'
                        })
                
                return filtered_data
            else:
                
                return []
        except Exception as e:
            
            return []

    def get_protocol_tvl(self, token_id: str) -> Dict:
        """
        Retrieves the Total Value Locked (TVL) for the specified protocol from DefiLlama.

        Args:
            token_id (str): The identifier of the protocol to query.

        Returns:
            Dict: A dictionary containing:
                - 'coin': The protocol's token identifier.
                - 'tvl': The formatted TVL value, or 'N/A' if data retrieval fails.
        """
        formatted_id = str(token_id).casefold()
        url = f"https://api.llama.fi/tvl/{formatted_id}"
        
        try:
            response = requests.get(url)
            if response.status_code == 200 and response.content:
                try:
                    data = response.json()
                    
                except json.JSONDecodeError:
                    
                    return {'coin': token_id, 'tvl': 'N/A'}

                tvl_value = data.get("tvl", 0) if isinstance(data, dict) else data
                formatted_tvl = self.format_number_short(number=tvl_value)
                return {'coin': token_id, 'tvl': formatted_tvl}
            else:
                
                return {'coin': token_id, 'tvl': 'N/A'}
        except Exception as e:
            
            return {'coin': token_id, 'tvl': 'N/A'}

    def format_number_short(self, number: Union[int, float]) -> str:
        """
        Formats a large number to a shorter string representation using suffixes (k, M, B, etc.).

        Args:
            number (Union[int, float]): The number to format.

        Returns:
            str: The formatted string representation of the number.
        """
        try:
            formatted_number = float(number)
        except (TypeError, ValueError):
            return "Invalid input"
        if formatted_number < 0:
            formatted_number = abs(formatted_number)
            negative_flag = True
        else:
            negative_flag = False
        suffixes = ['', 'k', 'M', 'B', 'T', 'P', 'E', 'Z', 'Y']
        suffix_index = 0
        while formatted_number >= 1000 and suffix_index < len(suffixes) - 1:
            formatted_number /= 1000.0
            suffix_index += 1
        formatted_string = '{:.3f}{}'.format(formatted_number, suffixes[suffix_index])
        if negative_flag:
            formatted_string = '-' + formatted_string
        return formatted_string
    
    def get_tvls_list(self):
        """
        Fetches market data for all chains
        Returns: Dictionary containing market data  
        """
        try:
            response = self.session.get(
                f"{self.BASE_URL_V2}/chains"
            )
            response.raise_for_status() 
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to fetch market data from Defillama: {str(e)}")
        
    def get_tvl_by_chain(self, chain_symbol: str):
        """
        Fetches TVL data for a specific chain
        Args:
            chain_symbol (str): Symbol of the chain
        Returns: Dictionary containing TVL data 
        """
        try:
            response = self.session.get(
                f"{self.BASE_URL_V2}/chains"
            )
            response.raise_for_status() 
            chains_tvl = response.json()
            for chain in chains_tvl:
                if chain['tokenSymbol'] == chain_symbol:
                    return chain
            return {}
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to fetch TVL data from Defillama: {str(e)}")
'''

# Initialize the service
llama_service = LlamaService()

@mcp.tool()
def get_chains_tvl() -> List[Dict]:
    """Get TVL data for major blockchain chains from DefiLlama"""
    return llama_service.get_llama_chains()

@mcp.tool()
def get_protocol_tvl(token_id: str) -> Dict:
    """Get TVL data for a specific DeFi protocol
    
    Args:
        token_id: The protocol identifier (e.g., 'uniswap', 'aave', 'lido')
    """
    return llama_service.get_protocol_tvl(token_id)

@mcp.tool()
def get_all_chains_tvl() -> List[Dict]:
    """Get TVL data for all chains from DefiLlama v2 API"""
    return llama_service.get_tvls_list()

@mcp.tool()
def get_chain_tvl_by_symbol(chain_symbol: str) -> Dict:
    """Get TVL data for a specific chain by its symbol
    
    Args:
        chain_symbol: The chain symbol (e.g., 'ETH', 'BTC', 'SOL')
    """
    return llama_service.get_tvl_by_chain(chain_symbol)

@mcp.tool()
def get_combined_tvl_data() -> List[Dict]:
    """Get combined TVL data for both chains and protocols of interest"""
    chains_data = llama_service.get_llama_chains()
    protocols_data = [llama_service.get_protocol_tvl(token_id=coin) for coin in llama_service.coins_protocol]
    return chains_data + protocols_data

if __name__ == "__main__":
    mcp.run(transport="stdio") 