# %% [markdown]

## Finetune LLM with QLoRA

# %% [markdown]

## Model

# In this notebook, we use an opensource model **Mistral 7B** as the pretrained model for finetuning. How it is trained is beyond hte scope of this notebook, but before jumping into modeling. I request everyone
# to go through the model documentation to understand the architecture and training process of the model. 
# 
# You can find the documentation [here](https://huggingface.co/mistral-7b-instruct-v0.1).   

# %% [markdown]

## Dataset

# In this notebook, we are fintetuning the model on the dataset **VIGGO** - a smaller but comprehensive dataset for instruction tuning. 
# It contains 10k instruction-response pairs, which is sufficient for finetuning a large language model with QLoRA. 
# 
# You can find the dataset [here](https://huggingface.co/datasets/mbzuai/viggo).

# %% [markdown]

## Installing dependencies

# %%

# !pip install peft==0.9.0
# !pip install -q -U transformers accelerate bitsandbytes
# !pip install -q tokenizers==0.15.2

# %% [markdown]

## Importing libraries

# %%

import os

os.environ["CUDA_LAUNCH_BLOCKING"] = "1"  # For debugging CUDA errors
os.environ["CUDA_VISIBLE_DEVICES"] = "0"  # Specify which GPU to use
os.environ["TOKENIZERS_PARALLELISM"] = "false"  # Disable parallelism in tokenizers to avoid warnings

# %% 
import torch
import transformers
from datetime import datetime
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from datasets import load_dataset
from accelerate import Accelerator
from peft import prepare_model_for_kbit_training, LoraConfig, PeftModel, get_peft_model

# %%

WORK_DIR = os.getenv("WORK_DIR", "/teamspace/studios/this_studio/finetuning-LLM-with-qlora")
MODEL_DIR = os.path.join(WORK_DIR, "data/hf-models/mistral/pytorch/7b-instruct-v0.1-hf/1")

# %%

with torch.no_grad():
    torch.cuda.empty_cache()
    
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}, {torch.cuda.get_device_name(0) if device.type == 'cuda' else 'CPU'}")
print(f"Total memory: {device}, {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB" if device.type == "cuda" else "N/A ")

# %% [markdown]

## Quantization configuration

# %% 

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16
)

# %% [markdown]

## Load the pretrained model and tokenizer

# %%

model = AutoModelForCausalLM.from_pretrained(MODEL_DIR, 
                                             quantization_config=bnb_config).to(device)

tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR,
                                          model_max_length=512,
                                          padding_side="left",
                                          add_eos_token=True)
tokenizer.pad_token = tokenizer.eos_token

# %% [markdown]

## Load dataset

# %% 

DATASET_PATH = os.path.join(WORK_DIR, "data/viggo-v1")

train_dataset = load_dataset(DATASET_PATH, split="train")
eval_dataset = load_dataset(DATASET_PATH, split="validation")
test_dataset = load_dataset(DATASET_PATH, split="test")

# %%

def tokenize(prompt):
    result = tokenizer(
        prompt,
        truncation=True,
        max_length=512,
        padding="max_length"
        # return_tensors="pt"
    )
    result["labels"] = result["input_ids"].copy()
    return result

# %%

def generate_and_tokenize_prompt(data_point):
    full_prompt=f"""Given a target sentence construct the underlying meaning representation of the input
    sentence as a single function with attributes and attribute values.
    This function should describe the target string accurately and the function must be one of the following
    ['inform', 'request', 'give_opinion', 'confirm', 'verify_attribute', 'suggest', 'request_explanation',
    'recommend', 'request_attribute'].
    The attributes must be one of the following: ['name', 'exp_release_date', 'release_year', 'developer',
    'esrb', 'rating', 'genres', 'player_perspective', 'has_multiplayer', 'platforms', 'available_on_steam',
    'has_linux_release', 'has_mac_release', 'specifier']
    
    ### Target sentence:
    {data_point["ref"]}
    
    ### Meaning representation:
    {data_point["mr"]}
    """
    
    return tokenize(full_prompt)

# %%
tokenized_train_dataset = train_dataset.map(generate_and_tokenize_prompt)
tokenized_eval_dataset = eval_dataset.map(generate_and_tokenize_prompt)
# tokenized_test_dataset = test_dataset.map(generate_and_tokenize_prompt)   

# %% 

print("Target Sentence: " + test_dataset[1]["ref"])
print("Meaning Representation: " + test_dataset[1]["mr"] + "\n")

# %% [markdown]

## Evaluate prompt

# %% 

eval_prompt=f"""Given a target sentence construct the underlying meaning representation of the input
sentence as a single function with attributes and attribute values.
This function should describe the target string accurately and the function must be one of the following
['inform', 'request', 'give_opinion', 'confirm', 'verify_attribute', 'suggest', 'request_explanation',
'recommend', 'request_attribute'].
The attributes must be one of the following: ['name', 'exp_release_date', 'release_year', 'developer',
'esrb', 'rating', 'genres', 'player_perspecive', 'has_multiplayer', 'platforms', 'available_on_steam',
'has_linux_release', 'has_mac_release', 'specifier']

### Target sentence:
Earlier, you stated that you didn't have strong feelings about PlayStation's Little Big Adventure. 
Is your opinion true for all games which don't have multiplayer?

### Meaning representation:
"""
# %%

model_input = tokenizer(eval_prompt, return_tensors="pt").to(device)
model.eval()

with torch.no_grad():
    output = model.generate( #ignore: pylint: disable=E1120
        input_ids=model_input.input_ids,
        attention_mask=model_input.attention_mask,
        max_new_tokens=256,
        pad_token_id=tokenizer.eos_token_id)
    print("Model output: " + tokenizer.decode(output[0], 
                                            skip_special_tokens=True))
    

# %% [markdown]

## Finetuning configuration

# %% 

model.gradient_checkpointing_enable()
model = prepare_model_for_kbit_training(model)

def print_trainable_parameters(model):
    trainable_params = 0
    all_param = 0
    for _, param in model.named_parameters():
        all_param += param.numel()
        if param.requires_grad:
            trainable_params += param.numel()
    print(
        f"Trainable parameters: {trainable_params} ({100 * trainable_params / all_param:.2f}%)"
    )

# %%

config = LoraConfig(
    r=8,
    lora_alpha=16,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj", "lm_head"],
    bias="none",
    lora_dropout=0.05, #Conventional
    task_type="CAUSAL_LM"
)

model = get_peft_model(model, config)
print_trainable_parameters(model)

# %% [markdown]

## Accelerator configuration

# %%

accelerator = Accelerator()
model = accelerator.prepare(model)
print_trainable_parameters(model)

# %% [markdown]

## Finetune the model

# %%

base_model_name = "mistral"
run_name = f"{base_model_name}-finetuned-{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}"
# run_name = f"{base_model_name}-finetuned-2026-05-18-19-34-15"
output_dir = os.path.join(MODEL_DIR, "outputs", run_name)

tokenizer.pad_token = tokenizer.eos_token

trainer = transformers.Trainer(
    model=model,
    train_dataset=tokenized_train_dataset,
    eval_dataset=tokenized_eval_dataset,
    args=transformers.TrainingArguments(
        output_dir=output_dir,
        warmup_steps=2,
        per_device_train_batch_size=8,
        gradient_accumulation_steps=4,
        max_steps=600,
        learning_rate=2e-4,
        logging_steps=50,
        fp16=True,
        optim="paged_adamw_8bit",
        logging_dir=os.path.join(output_dir, "logs"),
        save_strategy="steps",
        eval_steps=50,
        do_eval=True,
        report_to="none",
        run_name=run_name,
    ),
    data_collator=transformers.DataCollatorForSeq2Seq(tokenizer, pad_to_multiple_of=8, return_tensors="pt")
)

model.config.use_cache = False # silence the warnings. Please re-enable for inference!
trainer.train()

# %% [markdown]

## Load the trained base model

# %% 

base_model = AutoModelForCausalLM.from_pretrained(MODEL_DIR,
                                                  quantization_config=bnb_config,
                                                  device_map="auto",
                                                  trust_remote_code=True)

tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR,
                                          padding_side="left",
                                          add_eos_token=True,
                                          trust_remote_code=True)

tokenizer.pad_token = tokenizer.eos_token

# %% [markdown]

## Load the finetuned model

print("==================================================================================================")
print(f"Loading finetuned model from: " + os.path.join(MODEL_DIR, "outputs", run_name, "checkpoint-600"))

# %% 

ft_model = PeftModel.from_pretrained(base_model, model_id=os.path.join(MODEL_DIR, "outputs", run_name, "checkpoint-600")).to(device)
ft_model.eval()

# Normalize token id to a plain int to avoid Tensor typing/call issues.
eos_or_pad_token_id = tokenizer.eos_token_id
if isinstance(eos_or_pad_token_id, torch.Tensor):
    eos_or_pad_token_id = int(eos_or_pad_token_id.item())
elif eos_or_pad_token_id is None:
    eos_or_pad_token_id = tokenizer.pad_token_id
    
if isinstance(tokenizer.pad_token_id, torch.Tensor):
    tokenizer.pad_token_id = int(tokenizer.pad_token_id.item())

with torch.no_grad():
    output = ft_model.generate( #ignore: pylint: disable=E1120
                input_ids=model_input.input_ids,
                attention_mask=model_input.attention_mask,
                max_new_tokens=256,
                pad_token_id=int(eos_or_pad_token_id))
            
    print("Model output: " + tokenizer.decode(output[0], 
                                            skip_special_tokens=True,
                                            temperature=0.2,
                                            repetition_penalty=1.5))
    
print("==================================================================================================")