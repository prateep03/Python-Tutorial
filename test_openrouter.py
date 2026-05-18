#%% [markdown]
## Test OpenRouter Integration with OpenAI Python SDK
# %%
import os
import openai
import requests
import json
from openai import OpenAI

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# %% [markdown]

## Define OpenAI client (if needed)

# %%
try:
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY
    )
    print("OpenAI client initialized successfully.")
except Exception as e:
    print(f"Error initializing OpenAI client: {e}")



# %% 
response = client.chat.completions.create(
    model="openai/gpt-4.1-nano",
    messages=[
        {
            "role": "user",
            "content": "What is the meaning of life?"
        }
    ]
)

# %% 
print("Response from OpenRouter model:")
print(response.choices[0].message.content)
# %% [markdown]

# And now, let's ask for a question:

# %%
question = "Please propose a hard, challenging question to assess someone's IQ. Respond only with the question."
message = [{"role": "user", "content": question}]
# %%
question = client.chat.completions.create(
    model="openai/gpt-4.1-nano",
    messages=message
)

response = question.choices[0].message.content
# %% 
print("Challenging question:")
print(response)

# %% [markdown]
# Now, let's ask the challenging question we just received:

# %% 
response = client.chat.completions.create(
    model="openai/gpt-4.1-nano",
    messages=[{"role": "user", "content": response}]
)
print(response.choices[0].message.content)
# %% [markdown] 
from IPython.display import display, Markdown

display(Markdown(response.choices[0].message.content))

# %%