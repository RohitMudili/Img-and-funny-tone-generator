import os
import openai
from typing import Optional
import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ImageGenerator:
    def __init__(self, fal_ai_key: str, openai_key: str):
        self.fal_ai_key = fal_ai_key
        openai.api_key = openai_key
        self.model = "fal-ai/flux/schnell"
        
    def extract_visual_elements(self, text: str) -> str:
        """Extract visual elements from story text using OpenAI."""
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Extract key visual elements from the text that would make a good illustration. Focus on characters, settings, and key actions."},
                    {"role": "user", "content": text}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error extracting visual elements: {str(e)}")
            return text[:100]  # Fallback to first 100 characters
    
    def generate_story_image(self, story_text: str) -> Optional[str]:
        """Generate an image based on story content."""
        try:
            # Extract visual elements
            visual_elements = self.extract_visual_elements(story_text)
            
            # Create image prompt
            prompt = f"{visual_elements}, storybook illustration style, colorful, whimsical"
            
            # Generate image using Fal AI
            headers = {
                "Authorization": f"Key {self.fal_ai_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "prompt": prompt,
                "image_size": "landscape_4_3",
                "num_inference_steps": 4,
                "style": "storybook"
            }
            
            response = requests.post(
                f"https://fal.run/{self.model}",
                headers=headers,
                json=data
            )
            
            if response.status_code == 200:
                return response.json()["image"]["url"]
            else:
                logger.error(f"Fal AI API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error generating story image: {str(e)}")
            return None
    
    def generate_confused_image(self) -> Optional[str]:
        """Generate a fallback image for unrelated queries."""
        try:
            prompt = "A confused cartoon character scratching their head, question marks floating around, whimsical illustration"
            
            headers = {
                "Authorization": f"Key {self.fal_ai_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "prompt": prompt,
                "image_size": "landscape_4_3",
                "num_inference_steps": 4,
                "style": "storybook"
            }
            
            response = requests.post(
                f"https://fal.run/{self.model}",
                headers=headers,
                json=data
            )
            
            if response.status_code == 200:
                return response.json()["image"]["url"]
            else:
                logger.error(f"Fal AI API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error generating confused image: {str(e)}")
            return None 