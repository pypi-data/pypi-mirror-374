from google import genai
from google.genai import types

class AryGem:
    def __init__(self, api_key, model="gemini-2.5-flash"):
        self.client = genai.Client(api_key=api_key)
        self.model = model

    def generate(self, query, context=None):
        system_instruction = "You are a helpful assistant."
        if context:
            system_instruction += f" Use this context: {context}"

        response = self.client.models.generate_content(
            model=self.model,
            config=types.GenerateContentConfig(system_instruction=system_instruction),
            contents=query
        )
        return response.text
