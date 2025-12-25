from typing import List, Dict, Any, Optional
import json
from pydantic import BaseModel, Field
import os
from openai import OpenAI
from dotenv import load_dotenv
import hashlib

# Load environment variables
load_dotenv()

class Extractor:
    def __init__(self, model: str = "gpt-4o"):
        api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key) if api_key else None
        self.model = model
        self.cache = {}  # Simple in-memory cache

    def _get_cache_key(self, text: str) -> str:
        return hashlib.md5(text.encode()).hexdigest()

    def extract(self, text_content: str) -> List[Dict[str, Any]]:
        cache_key = self._get_cache_key(text_content)
        if cache_key in self.cache:
            print("Returning cached result")
            return self.cache[cache_key]

        if not self.client:
            return self._mock_extract(text_content)

        prompt = f"""
        You are an expert technical writer and information architect.
        Analyze the following documentation content and extract the key modules and submodules.
        
        STRICT OUTPUT FORMAT REQUIRED:
        You must return a JSON object with a single key "modules" containing an array of objects.
        Each object must have exactly these keys:
        - "module": The name of the module.
        - "Description": A detailed description of the module.
        - "Submodules": A dictionary where keys are submodule names and values are their detailed descriptions.
        - "confidence_score": A float between 0.0 and 1.0 indicating your confidence in this extraction.

        Example Output:
        {{
            "modules": [
                {{
                    "module": "Account Settings",
                    "Description": "Includes features and tools for managing account preferences.",
                    "Submodules": {{
                        "Change Username": "Explains how to update your handle."
                    }},
                    "confidence_score": 0.95
                }}
            ]
        }}

        Content to analyze (Length: {len(text_content)} chars):
        {text_content[:25000]}  # Truncate to avoid token limits
        """

        try:
            print(f"Sending request to OpenAI. Content length: {len(text_content)}")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that extracts structured information from documentation. You strictly follow JSON output formats."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            content = response.choices[0].message.content
            print(f"OpenAI Response: {content[:500]}...") # Log first 500 chars
            data = json.loads(content)
            
            # Normalize output
            result = []
            if isinstance(data, dict):
                # Look for "modules" key first
                if "modules" in data and isinstance(data["modules"], list):
                    result = data["modules"]
                else:
                    # Fallback: look for any list in the dict
                    for key in data:
                        if isinstance(data[key], list):
                            result = data[key]
                            break
            elif isinstance(data, list):
                result = data
            
            if not result:
                print("Warning: Extracted result is empty.")

            # Cache the result
            self.cache[cache_key] = result
            return result

        except Exception as e:
            # Re-raise the exception so the UI can display the actual error
            raise e

    def _mock_extract(self, text_content: str) -> List[Dict[str, Any]]:
        # Mock response for demonstration without API key
        return [
            {
                "module": "Account Management",
                "Description": "Features related to managing user accounts and profiles.",
                "Submodules": {
                    "Login/Signup": "Authentication processes for users.",
                    "Profile Settings": "Updating user information and preferences."
                },
                "confidence_score": 0.98
            },
            {
                "module": "Content Creation",
                "Description": "Tools for creating and publishing content.",
                "Submodules": {
                    "Post Editor": "Interface for writing and formatting posts.",
                    "Media Upload": "Uploading images and videos."
                },
                "confidence_score": 0.92
            }
        ]
