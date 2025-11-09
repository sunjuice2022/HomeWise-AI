"""
RAG (Retrieval-Augmented Generation) Engine for property data
"""
from typing import List, Dict, Any, Optional
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.docstore.document import Document
import os

from app.config import get_settings


class RAGEngine:
    """RAG engine for retrieving and generating property insights"""

    def __init__(self):
        """Initialize RAG engine"""
        self.settings = get_settings()
        self.embeddings = OpenAIEmbeddings(
            model=self.settings.embedding_model,
            openai_api_key=self.settings.openai_api_key
        )
        self.llm = ChatOpenAI(
            model=self.settings.openai_model,
            temperature=0.3,
            openai_api_key=self.settings.openai_api_key
        )
        self.vector_store: Optional[Chroma] = None
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.settings.chunk_size,
            chunk_overlap=self.settings.chunk_overlap
        )

    async def initialize(self, persist_directory: str = "./data/chroma_db"):
        """
        Initialize or load vector store

        Args:
            persist_directory: Directory to persist vector store
        """
        os.makedirs(persist_directory, exist_ok=True)

        # Try to load existing vector store
        if os.path.exists(persist_directory) and os.listdir(persist_directory):
            self.vector_store = Chroma(
                persist_directory=persist_directory,
                embedding_function=self.embeddings
            )
        else:
            # Create new vector store
            self.vector_store = Chroma(
                persist_directory=persist_directory,
                embedding_function=self.embeddings
            )

    def add_documents(self, documents: List[Dict[str, Any]]):
        """
        Add documents to vector store

        Args:
            documents: List of documents with 'content' and 'metadata' keys
        """
        if not self.vector_store:
            raise ValueError("Vector store not initialized")

        docs = []
        for doc in documents:
            # Split large documents into chunks
            chunks = self.text_splitter.split_text(doc.get("content", ""))

            for chunk in chunks:
                docs.append(
                    Document(
                        page_content=chunk,
                        metadata=doc.get("metadata", {})
                    )
                )

        if docs:
            self.vector_store.add_documents(docs)

    def add_property_data(self, property_data: Dict[str, Any]):
        """
        Add property data to vector store

        Args:
            property_data: Property information dictionary
        """
        # Create searchable content from property data
        content = f"""
        Property Address: {property_data.get('address', 'Unknown')}
        Suburb: {property_data.get('suburb', 'Unknown')}
        State: {property_data.get('state', 'Unknown')}
        Property Type: {property_data.get('property_type', 'Unknown')}
        Bedrooms: {property_data.get('bedrooms', 'N/A')}
        Bathrooms: {property_data.get('bathrooms', 'N/A')}
        Parking: {property_data.get('parking', 'N/A')}
        Land Size: {property_data.get('land_size', 'N/A')} sqm
        Last Sale Price: ${property_data.get('last_sale_price', 'N/A')}
        Last Sale Date: {property_data.get('last_sale_date', 'N/A')}
        Estimated Value: ${property_data.get('estimated_value', 'N/A')}
        """

        self.add_documents([{
            "content": content.strip(),
            "metadata": {
                **property_data,
                "type": "property_data"
            }
        }])

    def add_market_insight(self, insight: Dict[str, Any]):
        """
        Add market insight to vector store

        Args:
            insight: Market insight information
        """
        content = f"""
        Market Insight: {insight.get('title', 'Market Update')}
        Location: {insight.get('location', 'Australia')}
        Date: {insight.get('date', 'Recent')}

        {insight.get('content', '')}

        Key Points:
        {chr(10).join('- ' + point for point in insight.get('key_points', []))}
        """

        self.add_documents([{
            "content": content.strip(),
            "metadata": {
                **insight,
                "type": "market_insight"
            }
        }])

    async def search_similar_properties(
        self,
        query: str,
        k: int = 5,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar properties using vector similarity

        Args:
            query: Search query
            k: Number of results to return
            filter_dict: Metadata filters

        Returns:
            List of similar properties with scores
        """
        if not self.vector_store:
            raise ValueError("Vector store not initialized")

        # Build filter for property data only
        where_filter = {"type": "property_data"}
        if filter_dict:
            where_filter.update(filter_dict)

        results = self.vector_store.similarity_search_with_score(
            query=query,
            k=k,
            filter=where_filter
        )

        return [
            {
                "content": doc.page_content,
                "metadata": doc.metadata,
                "score": float(score)
            }
            for doc, score in results
        ]

    async def search_market_insights(
        self,
        query: str,
        k: int = 3,
        location: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for relevant market insights

        Args:
            query: Search query
            k: Number of results to return
            location: Filter by location

        Returns:
            List of relevant market insights
        """
        if not self.vector_store:
            raise ValueError("Vector store not initialized")

        where_filter = {"type": "market_insight"}
        if location:
            where_filter["location"] = location

        results = self.vector_store.similarity_search_with_score(
            query=query,
            k=k,
            filter=where_filter
        )

        return [
            {
                "content": doc.page_content,
                "metadata": doc.metadata,
                "score": float(score)
            }
            for doc, score in results
        ]

    async def query_with_context(
        self,
        question: str,
        context_type: str = "property",
        k: int = 3
    ) -> str:
        """
        Answer question using RAG

        Args:
            question: User's question
            context_type: Type of context ('property' or 'market')
            k: Number of context documents to retrieve

        Returns:
            Generated answer
        """
        if not self.vector_store:
            raise ValueError("Vector store not initialized")

        # Create custom prompt template
        template = """You are a knowledgeable Australian property expert.
        Use the following pieces of context to answer the question at the end.
        If you don't know the answer based on the context, say so - don't make up information.
        Always provide specific data points and sources when available.

        Context:
        {context}

        Question: {question}

        Answer:"""

        PROMPT = PromptTemplate(
            template=template,
            input_variables=["context", "question"]
        )

        # Create retrieval chain
        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vector_store.as_retriever(
                search_kwargs={
                    "k": k,
                    "filter": {"type": f"{context_type}_data" if context_type == "property" else "market_insight"}
                }
            ),
            chain_type_kwargs={"prompt": PROMPT}
        )

        # Get answer
        result = await qa_chain.ainvoke({"query": question})
        return result.get("result", "")

    def get_statistics(self) -> Dict[str, Any]:
        """Get vector store statistics"""
        if not self.vector_store:
            return {"status": "not_initialized"}

        collection = self.vector_store._collection
        return {
            "status": "initialized",
            "total_documents": collection.count(),
            "embedding_model": self.settings.embedding_model
        }
