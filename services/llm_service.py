from openai import OpenAI
import tiktoken
from config import settings

class Llm_Service:

    def __init__(self, model: str):
        self.model = model
        if model == "gpt-4o":
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        pass

    async def extract_data_from_llm(self, text: str, system_prompt = None):
        required_system_prompt = "Summarize the following text."
        if system_prompt:
            required_system_prompt = system_prompt
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": required_system_prompt},
                {"role": "user", "content": text}
            ]
        )
        return response.choices[0].message.content
    
    async def calculate_total_tokens(self, text: str):
        encoding = tiktoken.encoding_for_model(self.model)
        return len(encoding.encode(text))
    
    def split_text_into_token_chunks(text, model="gpt-4", max_tokens=1000, overlap=100):
        enc = tiktoken.encoding_for_model(model)
        tokens = enc.encode(text)

        chunks = []
        start = 0

        while start < len(tokens):
            end = start + max_tokens
            chunk_tokens = tokens[start:end]
            chunk_text = enc.decode(chunk_tokens)
            chunks.append(chunk_text)
            start += max_tokens - overlap
        return chunks