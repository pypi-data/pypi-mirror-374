import os
from typing import Optional, Dict, Any, List
import logging
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from dotenv import load_dotenv
load_dotenv()
class ModelWrapper:
    """Unified interface for different AI model providers."""
    
    def __init__(self, provider: str = "groq", model_name: str = "openai/gpt-oss-120b",api_key=None):
        self.provider = provider.lower()
        self.model_name = model_name
        self.api_key = api_key
        self.model = self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the appropriate model based on provider."""
        try:
            if self.provider == "openai":
                if not self.api_key:
                    raise ValueError("OpenAI API key not found in environment variables")
                return ChatOpenAI(
                    api_key=self.api_key,
                    model_name=self.model_name,
                    temperature=0.5
                )
            
            elif self.provider == "google":
                if not self.api_key:
                    raise ValueError("Google API key not found in environment variables")
                return ChatGoogleGenerativeAI(
                    google_api_key=self.api_key,
                    model=self.model_name,
                    temperature=0.5
                )
                
            elif self.provider == "groq":
                if not self.api_key:
                    raise ValueError("Groq API key not found in environment variables")
                return ChatGroq(
                    groq_api_key=self.api_key,
                    model_name=self.model_name,
                    temperature=0.5,
                    max_tokens = 2048
                )
            else:
                raise ValueError(f"Unsupported provider: {self.provider}")
                
        except Exception as e:
            raise
    def invoke(self,messages):
        response = self.model.invoke(messages)
        return response

def create_model(provider: str = None, model_name: str = None,api_key=None) -> ModelWrapper:
    """Factory function to create model instances with defaults from config."""
    return ModelWrapper(provider=provider, model_name=model_name,api_key=api_key)