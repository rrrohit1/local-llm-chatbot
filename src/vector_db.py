from pymilvus import connections, FieldSchema, CollectionSchema, DataType, Collection, utility
from sentence_transformers import SentenceTransformer

class MilvusChatDB:
    def __init__(self, host="localhost", port="19530"):
        """Initialize connection and collection in MilvusDB"""
        connections.connect("default", host=host, port=port)
        self.collection_name = "chat_history"

        # Define schema
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="timestamp", dtype=DataType.VARCHAR, max_length=50),
            FieldSchema(name="user_input", dtype=DataType.VARCHAR, max_length=500),
            FieldSchema(name="user_output", dtype=DataType.VARCHAR, max_length=500),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=384)
        ]
        schema = CollectionSchema(fields, description="Chat history with vector search")
        
        # Create collection
        self.collection = Collection(name=self.collection_name, schema=schema)
        self.collection.load()

        # Load embedding model
        self.model = SentenceTransformer("all-mpnet-base-v2")

    def add_entry(self, timestamp: str, user_input: str, user_output: str):
        """Insert a new chat record into Milvus"""
        embedding = self.model.encode(user_input).tolist()  # Convert text to vector
        data = [[None], [timestamp], [user_input], [user_output], [embedding]]
        
        insert_result = self.collection.insert(data)
        return insert_result.primary_keys  # Return inserted IDs

    def search_entry(self, query_text: str, top_k: int = 3):
        """Search similar user inputs in chat history"""
        query_embedding = self.model.encode(query_text).tolist()
        search_params = {"metric_type": "L2", "params": {"nprobe": 10}}

        results = self.collection.search(
            data=[query_embedding],
            anns_field="embedding",
            param=search_params,
            limit=top_k,
            output_fields=["timestamp", "user_input", "user_output"]
        )

        search_results = []
        for hits in results:
            for hit in hits:
                search_results.append({
                    "timestamp": hit.entity.get("timestamp"),
                    "user_input": hit.entity.get("user_input"),
                    "user_output": hit.entity.get("user_output"),
                    "score": hit.distance
                })
        
        return search_results  # Return list of similar chat entries

    def delete_entry(self, timestamp: str):
        """Delete a chat record based on timestamp"""
        expr = f'timestamp == "{timestamp}"'
        self.collection.delete(expr)

    def delete_instance(self):
        """Drop the Milvus collection"""
        utility.drop_collection(self.collection_name)
        print(f"Collection '{self.collection_name}' deleted.")

