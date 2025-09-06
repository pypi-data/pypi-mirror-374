import os
import pickle
from typing import Dict, List, Any, Optional
import logging
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.docstore.document import Document
from sentence_transformers import SentenceTransformer
import numpy as np

class PolicyRAGSystem:
    """RAG system for warranty policy validation."""
    
    def __init__(self, policy_dir: str , vector_db_dir: str,model_name:str="all-MiniLM-L6-v2",model_provider=None,api_key=None):
        self.policy_dir = policy_dir
        self.vector_db_dir = vector_db_dir
        self.embeddings = HuggingFaceEmbeddings(model_name=model_name)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100,
            length_function=len,
        )
        self.vector_store = None
        self.policy_documents = []
        os.makedirs(policy_dir, exist_ok=True)
        os.makedirs(vector_db_dir, exist_ok=True)
        self._load_or_create_vector_store()
    
    def _load_or_create_vector_store(self):
        """Load existing vector store or create new one."""
        vector_store_path = os.path.join(self.vector_db_dir, "policy_vector_store")
        
        try:
            if os.path.exists(vector_store_path):
                self.vector_store = FAISS.load_local(
                    vector_store_path, 
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
            else:
                self._create_vector_store()
        except Exception as e:
            self._create_vector_store()
    
    def _create_vector_store(self):
        """Create new vector store from policy documents."""
        try:
            documents = self._load_policy_documents()
            if documents:
                self.vector_store = FAISS.from_documents(documents, self.embeddings)
                vector_store_path = os.path.join(self.vector_db_dir, "policy_vector_store")
                self.vector_store.save_local(vector_store_path)
            else:
                print("No policy documents found")
                
        except Exception as e:
            print(f"Error creating vector store: {str(e)}")
    
    def _load_policy_documents(self) -> List[Document]:
        """Load and process policy documents."""
        documents = []
        
        try:
            for filename in os.listdir(self.policy_dir):
                if filename.endswith(('.txt', '.md')):
                    filepath = os.path.join(self.policy_dir, filename)
                    
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    chunks = self.text_splitter.split_text(content)
                    
                    for i, chunk in enumerate(chunks):
                        doc = Document(
                            page_content=chunk,
                            metadata={
                                'source': filename,
                                'chunk': i,
                                'policy_type': self._get_policy_type(filename)
                            }
                        )
                        documents.append(doc)
            return documents
            
        except Exception as e:
            return []
    
    def _get_policy_type(self, filename: str) -> str:
        """Determine policy type from filename."""
        filename_lower = filename.lower()
        if 'electronic' in filename_lower:
            return 'electronics'
        elif 'automotive' in filename_lower or 'auto' in filename_lower:
            return 'automotive'  
        elif 'general' in filename_lower:
            return 'general'
        else:
            return 'unknown'
    
    def search_relevant_policies(self, query: str, top_k: int = 8) -> List[Dict[str, Any]]:
        """Search for relevant policy information."""
        try:
            if not self.vector_store:
                return []
            
            results = self.vector_store.similarity_search_with_score(query, k=top_k)
            
            relevant_policies = []
            for doc, score in results:
                relevant_policies.append({
                    'content': doc.page_content,
                    'metadata': doc.metadata,
                    'relevance_score': float(score),
                    'source': doc.metadata.get('source', 'unknown')
                })
            
            return relevant_policies
            
        except Exception as e:
            return []
    
    def add_policy_document(self, filename: str, content: str):
        """Add new policy document to the system."""
        try:
            # Save document to policy directory
            filepath = os.path.join(self.policy_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Update vector store
            chunks = self.text_splitter.split_text(content)
            documents = []
            
            for i, chunk in enumerate(chunks):
                doc = Document(
                    page_content=chunk,
                    metadata={
                        'source': filename,
                        'chunk': i,
                        'policy_type': self._get_policy_type(filename)
                    }
                )
                documents.append(doc)
            if self.vector_store:
                self.vector_store.add_documents(documents)
            else:
                self.vector_store = FAISS.from_documents(documents, self.embeddings)
            
            # Save updated vector store
            vector_store_path = os.path.join(self.vector_db_dir, "policy_vector_store")
            self.vector_store.save_local(vector_store_path)
        except Exception as e:
            raise Exception(f"Error adding policy document: {str(e)}")