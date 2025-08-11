import os
from groq import Groq 


class GroqAIProcessor:
    def __init__(self , api_key):
        self.client = Groq(api_key=api_key,)

    def run_completion(self, user_input, context, last_conversation , prompt , model ):
        messages = [
            {
                "role": "system",
                "content": prompt  
            },
            {
                "role": "system",
                "content": f"Here is the customer's recent conversation history: {last_conversation}"
            },
            {
                "role": "system",
                "content": f"This is the context from the menu or knowledge base: {context}"
            },
            {
                "role": "user",
                "content": user_input
            }
        ]

        resp = self.client.chat.completions.create(
            messages=messages,
            model=model,
            temperature=0.0,
            top_p=1,
            max_tokens=1024
        )

        return resp.choices[0].message.content
    

if __name__ == '__main__':
    process = GroqAIProcessor()
    print(process.process_text('hello how are you'))