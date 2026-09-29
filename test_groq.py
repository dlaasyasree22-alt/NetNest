import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
g = Groq(api_key=os.environ["GROQ_API_KEY"])
r = g.chat.completions.create(
    model="openai/gpt-oss-120b",  # WHY this model: it's the doc's recommended one for function calling
    messages=[{"role": "user", "content": "Say hi in 5 words."}],
)
print(r.choices[0].message.content)
