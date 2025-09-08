from typing import Dict, Any, List, Optional
from arshai.core.interfaces.itool import ITool
from arshai.core.interfaces.ivector_db_client import IVectorDBClient, ICollectionConfig
from arshai.core.interfaces.iembedding import IEmbedding
import logging
import traceback

class KnowledgeBaseRetrievalTool(ITool):
    """Tool for retrieving knowledge from the vector database using both semantic and keyword-based search"""
    
    def __init__(self, 
                 vector_db: IVectorDBClient, 
                 embedding_model: IEmbedding,
                 collection_config: ICollectionConfig,
                 search_limit: int = 3):
        """
        Initialize the knowledge base retrieval tool.
        
        Args:
            vector_db: Vector database client for storing/retrieving embeddings
            embedding_model: Embedding model for converting queries to vectors
            collection_config: Complete collection configuration including field names and settings
            search_limit: Maximum number of results to return (default: 3)
        
        Example:
            from arshai.vector_db.milvus_client import MilvusClient
            from arshai.embeddings.openai_embeddings import OpenAIEmbedding
            from arshai.core.interfaces.iembedding import EmbeddingConfig
            from arshai.core.interfaces.ivector_db_client import ICollectionConfig
            
            # Create components directly
            vector_db = MilvusClient(host="localhost", port=19530)
            
            embedding_config = EmbeddingConfig(model_name="text-embedding-3-small")
            embedding_model = OpenAIEmbedding(embedding_config)
            
            collection_config = ICollectionConfig(
                collection_name="knowledge_base",
                dense_dim=1536,  # OpenAI embedding dimension
                text_field="content",
                metadata_field="metadata",
                is_hybrid=False  # Set to True if using hybrid search
            )
            
            # Create knowledge base tool
            kb_tool = KnowledgeBaseRetrievalTool(
                vector_db=vector_db,
                embedding_model=embedding_model,
                collection_config=collection_config,
                search_limit=5
            )
        """
        self.vector_db = vector_db
        self.embedding_model = embedding_model
        self.collection_config = collection_config
        self.search_limit = search_limit
        self.logger = logging.getLogger('KnowledgeBaseRetrievalTool')
        
        # Validate required components
        if not vector_db:
            self.logger.error("Vector database client not provided")
        if not embedding_model:
            self.logger.error("Embedding model not provided")
        if not collection_config:
            self.logger.error("Collection configuration not provided")
        
        if vector_db and embedding_model and collection_config:
            self.logger.info(f"Initialized knowledge base tool - Collection: {collection_config.collection_name}, "
                           f"Text field: {collection_config.text_field}, "
                           f"Metadata field: {collection_config.metadata_field}, "
                           f"Hybrid search: {collection_config.is_hybrid}, "
                           f"Search limit: {search_limit}")
            

    @property
    def function_definition(self) -> Dict:
        """Get the function definition for the LLM"""
        return {
            "name": "retrieve_knowledge",
            "description": "Retrieve relevant knowledge from the vector database using semantic and keyword search. The query MUST be self-contained and include all necessary context without relying on conversation history.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "A standalone, self-contained search query that includes all necessary context. The query will be processed using both dense and sparse vectors for semantic and keyword matching. Example of a good query: 'What are the fees for transferring money internationally using Taloan?' Instead of just 'What are the fees?'"
                    }
                },
                "required": ["query"],
                "additionalProperties": False
            }
        }

    def _format_search_results(self, search_results: List[Any]) -> str:
        """
        Format search results into a string for response
        
        Args:
            search_results: List of search results from vector database (Milvus Hits objects)
            
        Returns:
            str: Formatted string of relevant knowledge
        """
        if not search_results:
            return "No relevant information found."
            
        formatted_results = []
        
        # Each search_result is a Hits object containing multiple Hit objects
        for hits in search_results:
            # Log the number of hits in this result set
            self.logger.info(f"Processing result set with {len(hits)} hits")
            
            # Process each hit within the hits collection
            for hit in hits:
                try:
                    # Extract information from the hit
                    self.logger.debug(f"Processing hit with ID: {hit.id}, distance: {hit.distance}")
                    
                    # Extract text content - directly access the field value using hit.get()
                    text = hit.get(self.collection_config.text_field)
                    if text is None:
                        raise ValueError(f"Text field is None for hit ID: {hit.id}")
                    
                    # Extract metadata if available
                    metadata_field = self.collection_config.metadata_field
                    metadata = hit.get(metadata_field) if metadata_field in hit.fields else {}
                    if metadata is None:
                        metadata = {}
                    
                    source = metadata.get('source', 'unknown') if isinstance(metadata, dict) else 'unknown'
                    
                    # Format the result
                    formatted_results.append(f"Source: {source}\nContent: {text}\n")
                except Exception as e:
                    self.logger.error(f"Error processing hit: {str(e)}")
                    self.logger.error(traceback.format_exc())
        
        if not formatted_results:
            return "No relevant information could be extracted from the search results."
            
        return "\n".join(formatted_results)

    async def aexecute(self, query: str) -> List[Dict[str, Any]]:
        """
        Asynchronous execution of the knowledge retrieval using vector search
        
        Args:
            query: A standalone question containing all required context
            
        Returns:
            List[Dict[str, Any]]: List of content objects in the format required by the LLM
        """

        try:
            # Generate embeddings for the query
            query_embeddings = self.embedding_model.embed_document(query)
            
            # Perform vector search
            if self.collection_config.is_hybrid and 'sparse' in query_embeddings:
                # Use hybrid search if configuration supports it
                search_results = self.vector_db.hybrid_search(
                    config=self.collection_config,
                    dense_vectors=[query_embeddings['dense']],
                    sparse_vectors=[query_embeddings['sparse']],
                    limit=self.search_limit
                )
            else:
                # Use dense vector search only
                search_results = self.vector_db.search_by_vector(
                    config=self.collection_config,
                    query_vectors=[query_embeddings['dense']],
                    limit=self.search_limit
                )
            
            # Format the search results
            if search_results and len(search_results) > 0:
                formatted_text = self._format_search_results(search_results)
                return "function", [{"type": "text", "text": formatted_text}]
            else:
                return "function", [{"type": "text", "text": "No relevant information found."}]
                
        except Exception as e:
            self.logger.error(f"Error during vector search: {str(e)}")
            self.logger.error(f"Query embeddings type: {type(query_embeddings)}")
            if isinstance(query_embeddings, dict):
                self.logger.error(f"Query embeddings keys: {list(query_embeddings.keys())}")
            else:
                self.logger.error(f"Query embeddings content: {query_embeddings}")
            self.logger.error(traceback.format_exc())
            return "function", [{"type": "text", "text": f"Error retrieving knowledge: {str(e)}"}]

    def execute(self, query: str) -> List[Dict[str, Any]]:
        """
        Synchronous execution of the knowledge retrieval using vector search
        
        Args:
            query: A standalone question containing all required context
            
        Returns:
            List[Dict[str, Any]]: List of content objects in the format required by the LLM
        """

        try:
            # Generate embeddings for the query
            query_embeddings = self.embedding_model.embed_document(query)
            
            # Perform vector search
            if self.collection_config.is_hybrid and 'sparse' in query_embeddings:
                # Use hybrid search if configuration supports it
                search_results = self.vector_db.hybrid_search(
                    config=self.collection_config,
                    dense_vectors=[query_embeddings['dense']],
                    sparse_vectors=[query_embeddings['sparse']],
                    limit=self.search_limit
                )
            else:
                # Use dense vector search only
                search_results = self.vector_db.search_by_vector(
                    config=self.collection_config,
                    query_vectors=[query_embeddings['dense']],
                    limit=self.search_limit
                )
            
            # Format the search results
            if search_results and len(search_results) > 0:
                self.logger.info(f"search_results: {len(search_results)}")
                formatted_text = self._format_search_results(search_results)
                return "function", [{"type": "text", "text": formatted_text}]
            else:
                return "function", [{"type": "text", "text": "No relevant information found."}]
                
        except Exception as e:
            self.logger.error(f"Error during vector search: {str(e)}")
            self.logger.error(f"Query embeddings type: {type(query_embeddings)}")
            if isinstance(query_embeddings, dict):
                self.logger.error(f"Query embeddings keys: {list(query_embeddings.keys())}")
            else:
                self.logger.error(f"Query embeddings content: {query_embeddings}")
            self.logger.error(traceback.format_exc())
            return "function", [{"type": "text", "text": f"Error retrieving knowledge: {str(e)}"}]
