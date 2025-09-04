import faiss
import asyncio
from uuid import uuid4
from typing import List, Tuple, Sequence, Any, Union

from langchain_openai import OpenAIEmbeddings

from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI

from .configuration import Configuration
from .similarity_search.repository_faiss import VectorStorageRepositoryFAISS
from .schemas import Register


class MCPRouter:
    """
    A class that routes queries to the most relevant MCP (Model Context Protocol) tools
    using semantic similarity search and vector embeddings.
    """
    
    def __init__(self):
        """Initialize the MCP Router with configuration and vector stores."""
        self.config = Configuration()
        self.vector_store_name_groups = self.config.vector_store_groups_name
        self.vector_store_name_tools = self.config.vector_store_tools_name
        self.vector_store_groups = None
        self.vector_store_tools = None
        
    def initialize_index_groups(self):
        vector_store_groups = VectorStorageRepositoryFAISS(
            index_name=self.vector_store_name_groups
        )
        vector_store_groups.load_index()

        print(f'* Vector Store {self.vector_store_name_groups} does not exist, creating it...')
        
        registers_groups = []
        for mcp in self.config.mcps:
            mcp_group_name = mcp.get("group_name")
            mcp_group_description = mcp.get("group_description")

            register = Register(
                page_content=f"MCP Group: {mcp_group_name}\nMCP Description: {mcp_group_description}",
                metadata={"source": "groups", "group": mcp_group_name},
            )
            registers_groups.append(register)

        vector_store_groups.create_index(input_documents=registers_groups)
        
        self.vector_store_groups = vector_store_groups
        #print(f'* Vector Store {self.vector_store_name_groups} loaded successfully')

    def filter_documents_by_similarity(
        self,
        results: Sequence[Tuple[Any, Union[float, int]]],
        threshold: float,
        number_of_output_documents: int,
    ):
        if number_of_output_documents <= 0:
            return []

        if not results:
            return []

        # Ensure we are working with a list to allow multiple passes.
        sorted_results: List[Tuple[Any, Union[float, int]]] = sorted(results, key=lambda x: float(x[1]))

        # The best (lowest) score is our reference point.
        best_score = float(sorted_results[0][1])

        # Keep all results whose score is within `threshold` of the best score.
        filtered = [res for res in sorted_results if (float(res[1]) - best_score) < threshold]

        # Enforce the requested maximum length.
        return filtered[:number_of_output_documents]

    def find_relevant_groups(self, query: str):
        """Find the most relevant MCP groups for the given query."""
        # Similarity Search to get the most relevant group
        results = self.vector_store_groups.similarity_search_with_score(
            query,
            k=self.config.number_of_relevant_groups,
            filter={"source": "groups"},
        )

        # Filter Results to get the most relevant groups
        target_documents = self.filter_documents_by_similarity(
            results=results,
            threshold=self.config.threshold_for_relevant_groups,
            number_of_output_documents=self.config.number_of_filtered_groups
        )

        target_groups = [doc[0].metadata.get("group") for doc in target_documents]

        print(f"* Selected Groups: {target_groups}")
        
        return target_groups
    
    async def load_mcp_tools(self):
        """Load tools from the selected MCP groups."""
        mcp_groups = self.config.mcps

        mcp_tool_groups = {}
        for group in mcp_groups:
            group_name = group.get("group_name")
            for mcp in group.get("mcps"):
                # Load MCP
                mcp_name = mcp.get("name")
                client = MultiServerMCPClient({mcp_name: mcp.get("mcp_config")})

                # Load Tools
                tools = await client.get_tools()

                # Add Tools to Group
                if group_name not in mcp_tool_groups:
                    mcp_tool_groups[group_name] = []
                mcp_tool_groups[group_name].extend(tools)
            
        return mcp_tool_groups
    
    def initialize_index_tools(self, mcp_tool_groups):
        vector_store_tools = VectorStorageRepositoryFAISS(
            index_name=self.vector_store_name_tools
        )

        print(f'* Vector Store TOOLS {self.vector_store_name_tools} does not exist, creating it...')
        documents_tools = []
        for mcp_group, tools in mcp_tool_groups.items():
            for tool in tools:
                document = Register(
                    page_content=tool.description,
                    metadata={"source": mcp_group, "tool_name": tool.name},
                )
                documents_tools.append(document)
        
        vector_store_tools.create_index(input_documents=documents_tools)
        
        self.vector_store_tools = vector_store_tools

    def find_relevant_tools(self, query: str, target_groups):
        """Find the most relevant tools for the given query within target groups."""
        print(f'* Finding Relevant Tools...')
        print(f'* Target Groups: {target_groups}')

        # Similarity Search to get the most relevant tool
        input_args = {
            "query": query,
            "k": self.config.number_of_relevant_tools,
            "filter": {"source": {"$in": target_groups}}
        }

        target_documents = self.vector_store_tools.similarity_search(**input_args)

        target_tools = [doc.metadata.get("tool_name") for doc in target_documents]
        print(f'* Selected Tools: {target_tools}')
        
        return target_tools
    
    def select_target_tools(self, target_groups, target_tools, mcp_tool_groups):
        """Select the actual tool objects based on target tool names."""
        tools = []
        for group in target_groups:
            for tool in mcp_tool_groups.get(group):
                if tool.name in target_tools:
                    tools.append(tool)

        print(f'* Number of Target Tools: {len(tools)}')
        
        return tools
    
    def create_agent(self, tools):
        """Create the LangGraph ReAct agent with the selected tools."""
        model = ChatOpenAI(model=self.config.llm_model)
        prompt = """Use the available tools to answer questions. Do not use your own knowledge, only use the tools."""

        agent = create_react_agent(
            model, 
            tools,
            prompt=prompt
        )
        
        return agent

    async def smart_router(self, query: str):
        """
        Main method that routes a query to the most relevant MCP tools and returns the agent response.
        """
        # Step 1: Create and index group documents
        self.initialize_index_groups()
        
        # Step 2: Find relevant groups
        target_groups = self.find_relevant_groups(query)
        
        # Step 3: Load MCP tools from relevant groups
        mcp_tool_groups = await self.load_mcp_tools()
        
        # Step 4: Create and index tool documents
        self.initialize_index_tools(mcp_tool_groups)

        # Step 5: Find relevant tools
        target_tools = self.find_relevant_tools(query, target_groups)

        # Step 6: Select target tools
        tools = self.select_target_tools(target_groups, target_tools, mcp_tool_groups)

        # Step 7: Create agent
        agent = self.create_agent(tools)
        
        # Step 8: Invoke agent
        response = await agent.ainvoke({"messages": query})
        messages = response["messages"]

        print(f'* MCP Smart Router Agent Response: {messages}')

        return messages
    
    async def groups_router(self, query: str, target_groups: list[str] = None):
        """
        Main method that routes a query to the most relevant MCP tools and returns the agent response.
        
        Args:
            query (str): The user query to route and answer.
            
        Returns:
            The agent response messages.
        """
        # Step 1: Load MCP tools from relevant groups
        mcp_tool_groups = await self.load_mcp_tools()
        
        # Step 2: Create and index tool documents
        self.initialize_index_tools(mcp_tool_groups)
        
        # Step 3: Find relevant tools
        target_tools = self.find_relevant_tools(query, target_groups)
        
        # Step 4: Select target tools
        tools = self.select_target_tools(target_groups, target_tools, mcp_tool_groups)
        
        # Step 5: Create agent
        agent = self.create_agent(tools)
        
        # Step 6: Invoke agent
        response = await agent.ainvoke({"messages": query})
        messages = response["messages"]

        print(f'* MCP Groups Router Agent Response: {messages}')
        
        return messages


mcp_router = MCPRouter()
