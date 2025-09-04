import faiss
from uuid import uuid4

from langchain_openai import OpenAIEmbeddings

from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from ..schemas import Register

import asyncio

from .configuration import Configuration


class VectorStorageRepositoryFAISS:
    def __init__(self, index_name: str):
        self.config = Configuration()
        self.embeddings = OpenAIEmbeddings(model=self.config.embeddings_model)
        self.index_name = index_name
        self.path = f"./faiss_data/{self.index_name}"
        self.vector_store = None

    def create_index(self, input_documents: list[Register] = []):
        # Create index
        index = faiss.IndexFlatL2(len(self.embeddings.embed_query(self.index_name)))

        # Create vector store
        vector_store = FAISS(
            embedding_function=self.embeddings,
            index=index,
            docstore=InMemoryDocstore(),
            index_to_docstore_id={},
        )

        # Create documents
        documents = []
        for register in input_documents:
            document = Document(
                page_content=register.page_content,
                metadata=register.metadata
            )
            documents.append(document)

        # Add documents to vector store
        uuids = [str(uuid4()) for _ in range(len(documents))]
        vector_store.add_documents(documents=documents, ids=uuids)
        self.vector_store = vector_store

        # Save index
        self.save_index()

    def load_index(self):
        try:
            new_vector_store = FAISS.load_local(
                self.path, 
                self.embeddings,
                allow_dangerous_deserialization=True
            )
            self.vector_store = new_vector_store
        except Exception as e:
            print(f"No index found for {self.index_name}. Please create it first.")
            self.vector_store = None

    def save_index(self):
        self.vector_store.save_local(self.path)

    def delete_documents(self, document_ids: list[str]):
        self.vector_store.delete(ids=document_ids)

    def add_documents(self, documents: list[Register]):
        uuids = [str(uuid4()) for _ in range(len(documents))]
        self.vector_store.add_documents(documents=documents, ids=uuids)
        self.save_index()

    def similarity_search(self, query: str, k: int = 10, filter: dict = None):
        return self.vector_store.similarity_search(query, k=k, filter=filter)
    
    def similarity_search_with_score(self, query: str, k: int = 10, filter: dict = None):
        return self.vector_store.similarity_search_with_score(query, k=k, filter=filter)

