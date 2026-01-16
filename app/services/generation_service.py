"""Generation service for RAG using open-source LLMs."""

import asyncio
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from typing import List, Dict
from app.config import settings
from app.logging_config import logger


class GenerationService:
    """Service for generating claim analysis using an open-source LLM."""
    
    def __init__(self):
        """Initialize the generation service."""
        self.model = None
        self.tokenizer = None
        self._initialized = False
    
    async def initialize(self):
        """Initialize the LLM asynchronously."""
        if self._initialized:
            return
        
        logger.info(
            "Initializing LLM for generation",
            model_name=settings.llm_model,
            device=settings.llm_device
        )
        
        # Load model and tokenizer in executor
        loop = asyncio.get_event_loop()
        
        def load_model():
            tokenizer = AutoTokenizer.from_pretrained(settings.llm_model, trust_remote_code=True)
            if tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token
                
            model = AutoModelForCausalLM.from_pretrained(
                settings.llm_model,
                torch_dtype=torch.float32,
                device_map=settings.llm_device,
                trust_remote_code=True
            )
            return tokenizer, model

        self.tokenizer, self.model = await loop.run_in_executor(None, load_model)
        
        self._initialized = True
        logger.info("LLM initialized successfully")

    async def generate_analysis(
        self, 
        query: str, 
        retrieved_clauses: List[Dict]
    ) -> str:
        """
        Generate an analysis using the RAG pattern.
        
        Args:
            query: The user's claim description
            retrieved_clauses: List of relevant clauses from the vector store
            
        Returns:
            Generated analysis string
        """
        if not self._initialized:
            await self.initialize()
            
        if not retrieved_clauses:
            return "No relevant policy clauses were found to analyze this claim."

        # Construct the context from retrieved clauses
        context = "\n".join([
            f"- [{c['clause_id']}] {c['clause_text']}" 
            for c in retrieved_clauses
        ])
        
        # Construct a professional prompt
        prompt = (
            f"Instruct: You are an expert Insurance Policy Analyst. "
            f"Based on the following policy clauses, analyze the user's claim description. "
            f"State if it is likely covered and cite the clause ID.\n\n"
            f"POLICY CLAUSES:\n{context}\n\n"
            f"USER CLAIM: {query}\n\n"
            f"ANALYSIS:"
        )

        logger.info("Generating analysis for claim")
        
        loop = asyncio.get_event_loop()
        
        def run_generation():
            inputs = self.tokenizer(prompt, return_tensors="pt", padding=True).to(settings.llm_device)
            
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=settings.max_new_tokens,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=self.tokenizer.pad_token_id
                )
            
            full_response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            # Extract only the generated analysis part
            analysis = full_response.split("ANALYSIS:")[-1].strip()
            return analysis

        analysis = await loop.run_in_executor(None, run_generation)
        return analysis


# Global instance
generation_service = GenerationService()
