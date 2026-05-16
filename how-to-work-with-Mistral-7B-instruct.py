# %% [markdown]

# Specify the model path and load the tokenizer.

# %% 

MODEL_PATH = "/teamspace/studios/this_studio/hf-models/mistral/pytorch/7b-instruct-v0.1-hf/1"

# %% 

import os

os.environ["CUDA_LAUNCH_BLOCKING"] = "1"  # For debugging CUDA errors
os.environ["CUDA_VISIBLE_DEVICES"] = "0"  # Specify which GPU to use
os.environ["TOKENIZERS_PARALLELISM"] = "false"  # Disable parallelism in tokenizers to avoid warnings

# %% 

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

# %% [markdown]

# Clear torch cache and check for available devices.

# %%

with torch.no_grad():
    torch.cuda.empty_cache()
    
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}, {torch.cuda.get_device_name(0) if device.type == 'cuda' else 'CPU'}")
print(f"Total memory: {device}, {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB" if device.type == "cuda" else "N/A ")

# %% [markdown]

# Load the Mistral 7B Instruct model and tokenizer.

# %% 
model = AutoModelForCausalLM.from_pretrained(MODEL_PATH).to(device) 
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
# %% [markdown]

# Define a conversation with the model using the chat template and encode the messages for input to the model.

# %% 

def print_messages(messages):
    """Helper function to print messages in a readable format."""
    for msg in messages:
        print(f"{msg['role'].upper()}: {msg['content']}\n")
        
def model_chat(messages):
    """Function to generate a response from the model given a list of messages in the chat format."""
    print_messages(messages)
    encodeds = tokenizer.apply_chat_template(messages, return_tensors="pt")
    
    model_inputs = encodeds.to(device)
    
    generated_ids = model.generate( #ignore: pylint: disable=E1120
        input_ids=model_inputs.input_ids, 
        attention_mask=model_inputs.attention_mask,
        max_new_tokens=10000, 
        pad_token_id=tokenizer.eos_token_id,
        do_sample=True,
        top_p=0.9, 
        temperature=0.7)
    decoded = tokenizer.batch_decode(generated_ids,
                                     skip_special_tokens=True)
    return f"MODEL RESPONSE:\n{decoded[0]}\n"    

# %% [markdown]

# Example conversation with the model.

# %%
messages = [
    {"role": "user", "content": "What is your favorite condiment?"},
    {"role": "assistant", "content": "Well, I'm quite partial to a good squeeze of fresh lemon juice. It adds just the right amount of zesty flavor to whatever I'm cooking up in the kitchen"},
    {"role": "user", "content": "Do you have a mayonnaise receipe?"}
]

# %% [markdown]

# Generate responses from model.

# %% 
response = model_chat(messages)
print(response)

# %% [markdown]

# Generate a receipe for a vegetarian dish.

# %% 

messages = [
    {"role": "user", 
     "content": "Act as a gourmet chef. \
        I have a friend coming over who is a vegetarian. \
        Can you give me a recipe for a vegetarian dish that is easy to make and delicious?"
    }
]

response = model_chat(messages)
print(response)
# %%
