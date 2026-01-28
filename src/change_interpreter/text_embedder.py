import requests
import numpy as np
#import torch
import pickle
import os
from typing import Dict, List

class OllamaTextEncoder:
    def __init__(self, 
                 model="nomic-embed-text", 
                 host="http://localhost:11434",
                 cache_file="ollama_embeddings_cache.pkl"):
        """
        Initialize Ollama text encoder with caching
        
        Args:
            model: Ollama model name
            host: Ollama server address
            cache_file: Path to save/load embedding cache
        """
        self.model = model
        self.host = host
        self.cache_file = cache_file
        self.embedding_cache = {}
        
        # Load existing cache if available
        self.load_cache()
        
        # Get embedding dimension
        if not self.embedding_cache:
            self.embedding_dim = self._get_embedding_dim()
        else:
            # Get dimension from cached embedding
            sample_emb = next(iter(self.embedding_cache.values()))
            self.embedding_dim = len(sample_emb)
        
        print(f"✓ Ollama encoder initialized")
        print(f"  Model: {self.model}")
        print(f"  Embedding dimension: {self.embedding_dim}")
        print(f"  Cached embeddings: {len(self.embedding_cache)}")
    
    def _get_embedding_dim(self):
        """Detect embedding dimension by making test call"""
        test_emb = self._call_ollama("test")
        return len(test_emb)
    
    def _call_ollama(self, text):
        """Make API call to Ollama"""
        try:
            response = requests.post(
                f"{self.host}/api/embeddings",
                json={
                    "model": self.model,
                    "prompt": text
                },
                timeout=30
            )
            
            if response.status_code == 200:
                return np.array(response.json()["embedding"])
            else:
                print(f"Error {response.status_code}: {response.text}")
                return np.zeros(self.embedding_dim)
                
        except requests.exceptions.ConnectionError:
            print(f"Error: Cannot connect to Ollama at {self.host}")
            print("Make sure Ollama is running: 'ollama serve'")
            return np.zeros(self.embedding_dim)
        except Exception as e:
            print(f"Error calling Ollama: {e}")
            return np.zeros(self.embedding_dim)
    
    def get_embedding(self, text):
        """Get embedding for single text with caching"""
        if not text or text == '$':
            if '$' not in self.embedding_cache:
                self.embedding_cache['$'] = np.zeros(self.embedding_dim)
            return self.embedding_cache['$']
        
        # Check cache first
        if text in self.embedding_cache:
            return self.embedding_cache[text]
        
        # Call Ollama API
        embedding = self._call_ollama(text)
        
        # Cache result
        self.embedding_cache[text] = embedding
        
        return embedding
    
    def precompute_all_embeddings(self, all_patches):
        """
        ONE-TIME: Compute embeddings for all unique texts in your dataset
        This avoids repeated API calls during training
        """
        # Collect unique texts
        unique_texts = set()
        
        for patch in all_patches:
            for timestamp in ['0', '1']:
                if timestamp in patch:
                    for node_id, node_data in patch[timestamp].items():
                        props = node_data['properties']
                        
                        name = props.get('Name', '$')
                        category = props.get('Category', '$')
                        description = props.get('Description', '$')
                        
                        if name != '$':
                            unique_texts.add(name)
                        if category != '$':
                            unique_texts.add(category)
                        if description != '$':
                            unique_texts.add(description)
        
        # Remove already cached texts
        texts_to_embed = [t for t in unique_texts if t not in self.embedding_cache]
        
        if not texts_to_embed:
            print("✓ All texts already cached!")
            return
        
        print(f"Computing embeddings for {len(texts_to_embed)} unique texts...")
        print(f"(This will take ~{len(texts_to_embed) * 0.05:.1f} seconds)")
        
        # Embed each text
        for i, text in enumerate(texts_to_embed):
            if i % 10 == 0:
                print(f"  Progress: {i}/{len(texts_to_embed)}")
            
            embedding = self._call_ollama(text)
            self.embedding_cache[text] = embedding
        
        # Add zero embedding for null
        self.embedding_cache['$'] = np.zeros(self.embedding_dim)
        
        # Save cache
        self.save_cache()
        
        print(f"✓ Precomputation complete!")
        print(f"  Total cached embeddings: {len(self.embedding_cache)}")
    
    def save_cache(self):
        """Save embedding cache to disk"""
        with open(self.cache_file, 'wb') as f:
            pickle.dump(self.embedding_cache, f)
        print(f"✓ Cache saved to {self.cache_file}")
    
    def load_cache(self):
        """Load embedding cache from disk"""
        if os.path.exists(self.cache_file):
            with open(self.cache_file, 'rb') as f:
                self.embedding_cache = pickle.load(f)
            print(f"✓ Loaded {len(self.embedding_cache)} cached embeddings from {self.cache_file}")


    def encode_test(self, word, word1):
        name_emb = self.get_embedding(word)
        cat_emb = self.get_embedding(word1)
        print(name_emb)
        print(cat_emb)

        combined = (name_emb + cat_emb)/2
        print(combined)
    
    def encode_text_properties(self, node_data):
        """
        Encode Name and Category fields from node data
        Returns concatenated or averaged embedding
        """
        props = node_data.get('properties', node_data)
        
        name = props.get('Name', '$')
        category = props.get('Category', '$')
        
        # Get embeddings (from cache or API)
        name_emb = self.get_embedding(name)
        category_emb = self.get_embedding(category)
        
        # Option 1: Average (recommended - keeps dimension same)
        combined = (name_emb + category_emb) / 2
        
        # Option 2: Concatenate (doubles dimension)
        # combined = np.concatenate([name_emb, category_emb])
        
        #### TO DO######
        ##### import pytorch
        #return torch.tensor(combined, dtype=torch.float)
        return combined
    

    
    def batch_encode_texts(self, texts: List[str]) -> List[np.ndarray]:
        """
        Encode multiple texts (useful for precomputation)
        Note: Ollama doesn't have native batch API, so this calls sequentially
        """
        embeddings = []
        for text in texts:
            embeddings.append(self.get_embedding(text))
        return embeddings