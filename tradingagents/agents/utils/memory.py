import chromadb
from chromadb.config import Settings
import hashlib
import numpy as np


class FinancialSituationMemory:
    def __init__(self, name, config):
        self.config = config
        self.use_embeddings = False
        
        # Only use embeddings if OpenAI or local Ollama backend
        if config["backend_url"] == "http://localhost:11434/v1":
            try:
                from openai import OpenAI
                self.embedding = "nomic-embed-text"
                self.client = OpenAI(base_url=config["backend_url"])
                self.use_embeddings = True
            except:
                self.use_embeddings = False
        elif config["backend_url"] == "https://api.openai.com/v1":
            try:
                from openai import OpenAI
                self.embedding = "text-embedding-3-small"
                self.client = OpenAI(base_url=config["backend_url"])
                self.use_embeddings = True
            except:
                self.use_embeddings = False
        else:
            # For Google/Gemini and other backends, use simple hash-based embeddings
            self.use_embeddings = False
            
        self.chroma_client = chromadb.Client(Settings(allow_reset=True))
        self.situation_collection = self.chroma_client.create_collection(name=name)

    def get_embedding(self, text):
        """Get embedding for a text - uses OpenAI if available, else simple hash"""
        if self.use_embeddings:
            try:
                response = self.client.embeddings.create(
                    model=self.embedding, input=text
                )
                return response.data[0].embedding
            except Exception as e:
                # Fallback to hash-based embedding if API fails
                return self._get_hash_embedding(text)
        else:
            return self._get_hash_embedding(text)
    
    def _get_hash_embedding(self, text):
        """Create a simple deterministic embedding from text using hashing"""
        # Create a 384-dimensional embedding (smaller than typical 1536)
        # This is a simple fallback when real embeddings aren't available
        text_hash = hashlib.sha256(text.encode()).hexdigest()
        
        # Convert hash to numbers
        embedding = []
        for i in range(0, min(len(text_hash), 384*2), 2):
            # Convert hex pairs to float values between -1 and 1
            hex_val = int(text_hash[i:i+2], 16)
            normalized = (hex_val / 128.0) - 1.0
            embedding.append(normalized)
        
        # Pad to 384 dimensions if needed
        while len(embedding) < 384:
            embedding.append(0.0)
            
        return embedding[:384]

    def add_situations(self, situations_and_advice):
        """Add financial situations and their corresponding advice. Parameter is a list of tuples (situation, rec)"""

        situations = []
        advice = []
        ids = []
        embeddings = []

        offset = self.situation_collection.count()

        for i, (situation, recommendation) in enumerate(situations_and_advice):
            situations.append(situation)
            advice.append(recommendation)
            ids.append(str(offset + i))
            embeddings.append(self.get_embedding(situation))

        self.situation_collection.add(
            documents=situations,
            metadatas=[{"recommendation": rec} for rec in advice],
            embeddings=embeddings,
            ids=ids,
        )

    def get_memories(self, current_situation, n_matches=1):
        """Find matching recommendations using OpenAI embeddings"""
        query_embedding = self.get_embedding(current_situation)

        results = self.situation_collection.query(
            query_embeddings=[query_embedding],
            n_results=n_matches,
            include=["metadatas", "documents", "distances"],
        )

        matched_results = []
        for i in range(len(results["documents"][0])):
            matched_results.append(
                {
                    "matched_situation": results["documents"][0][i],
                    "recommendation": results["metadatas"][0][i]["recommendation"],
                    "similarity_score": 1 - results["distances"][0][i],
                }
            )

        return matched_results


if __name__ == "__main__":
    # Example usage
    matcher = FinancialSituationMemory()

    # Example data
    example_data = [
        (
            "High inflation rate with rising interest rates and declining consumer spending",
            "Consider defensive sectors like consumer staples and utilities. Review fixed-income portfolio duration.",
        ),
        (
            "Tech sector showing high volatility with increasing institutional selling pressure",
            "Reduce exposure to high-growth tech stocks. Look for value opportunities in established tech companies with strong cash flows.",
        ),
        (
            "Strong dollar affecting emerging markets with increasing forex volatility",
            "Hedge currency exposure in international positions. Consider reducing allocation to emerging market debt.",
        ),
        (
            "Market showing signs of sector rotation with rising yields",
            "Rebalance portfolio to maintain target allocations. Consider increasing exposure to sectors benefiting from higher rates.",
        ),
    ]

    # Add the example situations and recommendations
    matcher.add_situations(example_data)

    # Example query
    current_situation = """
    Market showing increased volatility in tech sector, with institutional investors 
    reducing positions and rising interest rates affecting growth stock valuations
    """

    try:
        recommendations = matcher.get_memories(current_situation, n_matches=2)

        for i, rec in enumerate(recommendations, 1):
            print(f"\nMatch {i}:")
            print(f"Similarity Score: {rec['similarity_score']:.2f}")
            print(f"Matched Situation: {rec['matched_situation']}")
            print(f"Recommendation: {rec['recommendation']}")

    except Exception as e:
        print(f"Error during recommendation: {str(e)}")
