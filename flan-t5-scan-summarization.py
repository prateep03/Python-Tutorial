# %% [markdown]

# # Fine-tune FLAN-T5 for chat & dialogue summarization
# 
# In this blog, you will learn how to fine-tune [google/flan-t5-xl](https://huggingface.co/google/flan-t5-xl) for chat & dialogue summarization using Hugging Face Transformers. If you already know T5, FLAN-T5 is just better at everything. For the same number of parameters, these models have been fine-tuned on more than 1000 additional tasks covering also more languages. 
# 
# In this example we will use the [samsum](https://huggingface.co/datasets/samsum) dataset a collection of about 16k messenger-like conversations with summaries. Conversations were created and written down by linguists fluentin English.
# 
# You will learn how to:
# 
# 1. [Setup Development Environment](#1-setup-development-environment)
# 2. [Load and prepare samsum dataset](#2-load-and-prepare-samsum-dataset)
# 3. [Fine-tune and evaluate FLAN-T5](#3-fine-tune-and-evaluate-flan-t5)
# 4. [Run Inference and summarize ChatGPT dialogues](#4-run-inference-and-summarize-chatgpt-dialogues)
# 
# Before we can start, make sure you have a [Hugging Face Account](https://huggingface.co/join) to save artifacts and experiments. 

# %% [markdown]

# ## Quick intro: FLAN-T5, just a better T5
# 
# FLAN-T5 released with the [Scaling Instruction-Finetuned Language Models](https://arxiv.org/pdf/2210.11416.pdf) paper is an enhanced version of T5 that has been finetuned in a mixture of tasks. The paper explores instruction finetuning with a particular focus on (1) scaling the number of tasks, (2) scaling the model size, and (3) finetuning on chain-of-thought data. The paper discovers that overall instruction finetuning is a general method for improving the performance and usability of pretrained language models. 
# 
# ![flan-t5](../assets/flan-t5.png)
# 
# * Paper: https://arxiv.org/abs/2210.11416
# * Official repo: https://github.com/google-research/t5x
# 
# --- 
# 
# Now we know what FLAN-T5 is, let's get started. 🚀
# 
# _Note: This tutorial was created and run on a g4dn.xlarge AWS EC2 Instance including a NVIDIA T4._

# %% 


import os

os.environ["CUDA_LAUNCH_BLOCKING"] = "1"  # For debugging CUDA errors
# os.environ["CUDA_VISIBLE_DEVICES"] = "1"  # Specify which GPU to use


# ## 1. Setup Development Environment
# 
# Our first step is to install the Hugging Face Libraries, including transformers and datasets. Running the following cell will install all the required packages. 

# In[36]:


# python
#!pip install pytesseract transformers datasets rouge-score nltk tensorboard py7zr --upgrade


# %% [markdown]

# install git-fls for pushing model and logs to the hugging face hub

#!sudo apt-get install git-lfs --yes


# This example will use the [Hugging Face Hub](https://huggingface.co/models) as a remote model versioning service. To be able to push our model to the Hub, you need to register on the [Hugging Face](https://huggingface.co/join). 
# 
# If you already have an account, you can skip this step. 
#
# After you have an account, we will use the `notebook_login` util from the `huggingface_hub` package to log into our account and store our token (access key) on the disk. 


# %% 

from dotenv import load_dotenv

load_dotenv(override=True)


# %% 

hf_token = os.getenv("HUGGINGFACE_API_KEY")
assert hf_token is not None, "HUGGINGFACE_API_KEY not found in environment variables"
print(f"Hugging Face token found: {hf_token}")


# %% 

from huggingface_hub import notebook_login, login

# notebook_login()
login(token=hf_token)


# Check token is loaded.

# %% 

from huggingface_hub import whoami

print(whoami())
hf_username = whoami(token=hf_token)["name"]
print(f"Hugging Face username: {hf_username}")


# ## 2. Load and prepare scan dataset

# %%

import pandas as pd
import numpy as np

# %% [markdown]

# Patch for torch._six compabitlity issue

# %% 
import sys
import math
import torch

# Create torch._six module if it doesn't exist
if 'torch._six' not in sys.modules:
    from types import ModuleType
    
    six_module = ModuleType('_six')
    six_module.inf = math.inf
    torch._six = six_module
    sys.modules['torch._six'] = six_module
    
if torch.cuda.is_available():
    torch.cuda.empty_cache()
    
    # Rese peak memory stats
    torch.cuda.reset_peak_memory_stats()
    torch.cuda.reset_accumulated_memory_stats()

# %% [markdown]

# __Available Variants__

# Google has released the following FLAN-T5 variants on Hugging Face, differing in size and parameter count: 

# - google/flan-t5-small (77M parameters)
# - google/flan-t5-base (250M parameters)
# - google/flan-t5-large (800M parameters)
# - google/flan-t5-xl (3B parameters)
# - google/flan-t5-xxl (11B parameters) 

# %%

DATA_DIR = "/teamspace/studios/this_studio/data"
XLS_PATH = os.path.join(DATA_DIR, "print_output_with_recommendation_hybrid.xlsx")
MODEL_ID = "google/flan-t5-large"  # change to your preferred model size
PROMPT_TEMPLATE = "summarize the following document scan text:\n\n{input_text}\n\nSummary:"
TEXT_COLUMN = "prompt"
SUMMARY_COLUMN = "recommendation"
RANDOM_SEED = 42

# %% 

if not os.path.exists(XLS_PATH):
    raise FileNotFoundError(f"File not found: {XLS_PATH}")

if str(XLS_PATH).endswith(".xlsx"):
    print(f"Loading data from Excel file: {XLS_PATH}")
    data = pd.read_excel(XLS_PATH).dropna(subset=["generated_prompt", "recommendation"])
elif str(XLS_PATH).endswith(".csv"):
    print(f"Loading data from CSV file: {XLS_PATH}")
    data = pd.read_csv(XLS_PATH).dropna(subset=["generated_prompt", "recommendation"])
else:
    raise ValueError("Unsupported file format. Please provide an .xlsx or .csv file.")

print(f"Loaded {len(data)} samples")


# %%

# rename `generated_prompt` to `prompt` and `recommendation` to `summary`
data = data.rename(columns={"generated_prompt": TEXT_COLUMN, "recommendation": SUMMARY_COLUMN})

# %% [markdown]

# ### 2.1 Group recommendations into categories to enabe stratified splitting

# %%

data["recommendation_category"] = data[SUMMARY_COLUMN].apply(lambda x: x.split()[0] if isinstance(x, str) and len(x.split()) > 0 else "unknown")

# %% [markdown]

# ### 2.2 Split into train and test subsets. 
# 
# Split entire dataset into `train` and `test` splits. Create a dictionary `dataset` with keys `train` and `test` to hold the two subsets.

# %%

from sklearn.model_selection import train_test_split
from datasets import Dataset, DatasetDict

# Split data into train and test (80/20 split)
train_data, test_data = train_test_split(data, test_size=0.1, 
                                         random_state=RANDOM_SEED,
                                         stratify=data["recommendation_category"])

print(f"Train samples: {len(train_data)}")
print(f"Test samples: {len(test_data)}")

# Create dataset dictionary with train and test splits

dataset = DatasetDict({
    "train": Dataset.from_pandas(train_data.reset_index(drop=True)),
    "test": Dataset.from_pandas(test_data.reset_index(drop=True))
})

print(f"Train dataset size: {len(dataset['train'])}")
print(f"Test dataset size: {len(dataset['test'])}")


# %% [markdown]

# Lets checkout an example of the dataset.

# %%

import random
from random import randrange

random.seed(42)

sample = dataset['train'][randrange(len(dataset['train']))]
print(f"prompt: \n{sample[TEXT_COLUMN]}\n--------------------")
print(f"summary: \n{sample[SUMMARY_COLUMN]}\n")

# %% [markdown]

### 2.3 Tokenize dataset

# To train our model we need to convert our inputs (text) to token IDs. This is done by a 🤗 Transformers Tokenizer. 
# If you are not sure what this means check out [chapter 6](https://huggingface.co/course/chapter6/1?fw=tf) of the Hugging Face Course.

# %%

from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# Load tokenizer of `model_id` from the Hugging Face Hub
tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, 
                                          trust_remote_code=True)

# Move model to GPU
if torch.cuda.is_available():
    device = torch.device("cuda")
else:
    device = torch.device("cpu")

print(f"Device: {device}")

# %% [markdown]

### 2.4 Calculate max sample length

# We defined a `PROMPT_TEMPLATE` in our config, which we will use to construct an instruct prompt for better performance of our model.
#
# Our `PROMPT_TEMPLATE` has a "fixed" start and end, and our document is in the middle. This means we need to ensure that the "fixed"
# template parts + document are not exceeding the max length of our model. 
#
# Therefore, we calculate the max length of our document,
# which we will use later for truncation during tokenization.

# %% 

prompt_length = len(tokenizer(PROMPT_TEMPLATE.format(input_text=""))["input_ids"])
max_sample_length = tokenizer.model_max_length - prompt_length
print(f"Prompt length: {prompt_length}")
print(f"Max sample length: {max_sample_length}")


# %% [markdown]
# Before we can start training we need to preprocess our data. Abstractive Summarization is a text2text-generation task. 
# This means our model will take a text as input and generate a summary as output. For this we want to understand how long our input and output will be 
# to be able to efficiently batch our data. 

# %%

from datasets import concatenate_datasets

# The maximum total input sequence length after tokenization. 
# Sequences longer than this will be truncated, sequences shorter will be padded.
tokenized_inputs = concatenate_datasets([dataset["train"], dataset["test"]]).map(lambda x: tokenizer(x[TEXT_COLUMN], truncation=True), batched=True, remove_columns=[TEXT_COLUMN, SUMMARY_COLUMN])
max_source_length = max([len(x) for x in tokenized_inputs["input_ids"]])
max_source_length = min(max_source_length, max_sample_length)
print(f"Max source length: {max_source_length}")

# The maximum total sequence length for target text after tokenization. 
# Sequences longer than this will be truncated, sequences shorter will be padded."
tokenized_targets = concatenate_datasets([dataset["train"], dataset["test"]]).map(lambda x: tokenizer(x[SUMMARY_COLUMN], truncation=True), batched=True, remove_columns=[TEXT_COLUMN, SUMMARY_COLUMN])
max_target_length = max([len(x) for x in tokenized_targets["input_ids"]])
max_target_length = min(max_target_length, 128)  # we set a hard limit of 128 for summaries
print(f"Max target length: {max_target_length}")


# In[51]:


def preprocess_function(sample,padding="max_length"):

    # add prefix to the input for t5
    inputs = [PROMPT_TEMPLATE.format(input_text=doc) for doc in sample[TEXT_COLUMN]]

    # tokenize inputs
    model_inputs = tokenizer(inputs, max_length=max_source_length, padding=padding, truncation=True)

    # Tokenize targets with the `text_target` keyword argument
    labels = tokenizer(text_target=sample[SUMMARY_COLUMN], max_length=max_target_length, padding=padding, truncation=True)

    # If we are padding here, replace all tokenizer.pad_token_id in the labels by -100 when we want to ignore
    # padding in the loss.
    if padding == "max_length":
        labels["input_ids"] = [
            [(l if l != tokenizer.pad_token_id else -100) for l in label] for label in labels["input_ids"]
        ]

    model_inputs["labels"] = labels["input_ids"]
    return model_inputs

tokenized_dataset = dataset.map(preprocess_function, batched=True, 
                                    remove_columns=[TEXT_COLUMN, SUMMARY_COLUMN, "recommendation_category",
                                                    "engineType", "Color", "DocumentType&Frequency", 
                                                    "finisher", "Duplexer", "Industry"])
print(f"Keys of tokenized dataset: {list(tokenized_dataset['train'].features)}")


# %% [markdown]
# ## 3. Fine-tune and evaluate FLAN-T5
# 
# After we have processed our dataset, we can start training our model. Therefore we first need to load our [FLAN-T5](https://huggingface.co/models?search=flan-t5) from the Hugging Face Hub. In the example we are using a instance with a NVIDIA V100 meaning that we will fine-tune the `base` version of the model. 
# _I plan to do a follow-up post on how to fine-tune the `xxl` version of the model using Deepspeed._
# 

# %%

from transformers import AutoModelForSeq2SeqLM

# load model from the hub
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_ID,
                                              ignore_mismatched_sizes=True,
                                              trust_remote_code=True)

model.gradient_checkpointing_enable() # Enable gradient checkpointing to save memory during training

# Move model to GPU
if torch.cuda.is_available():
    device = torch.device("cuda")
    model = model.to(device)
    print(f"Model moved to GPU: {torch.cuda.get_device_name(0)}")
    print(f"GPU memory allocated: {torch.cuda.memory_allocated(0) / 1024**3:.2f} GB")
else:
    device = torch.device("cpu")
    model = model.to(device)
    print("CUDA not available, using CPU")

# We want to evaluate our model during training. The `Trainer` supports evaluation during training by providing a `compute_metrics`.  
# The most commonly used metrics to evaluate summarization task is [rogue_score](https://en.wikipedia.org/wiki/ROUGE_(metric)) short for Recall-Oriented Understudy for Gisting Evaluation). This metric does not behave like the standard accuracy: it will compare a generated summary against a set of reference summaries
# 
# We are going to use `evaluate` library to evaluate the `rogue` score.

# %%

import evaluate #ignore: pylint: disable=import-error
import nltk #ignore: pylint: disable=import-error
import numpy as np
from nltk.tokenize import sent_tokenize #ignore: pylint: disable=import-error
nltk.download("punkt")

# Metric
metric = evaluate.load("rouge")

# helper function to postprocess text
def postprocess_text(preds, labels):
    preds = [pred.strip() for pred in preds]
    labels = [label.strip() for label in labels]

    # rougeLSum expects newline after each sentence
    preds = ["\n".join(sent_tokenize(pred)) for pred in preds]
    labels = ["\n".join(sent_tokenize(label)) for label in labels]

    return preds, labels

def compute_metrics(eval_preds):
    preds, labels = eval_preds
    if isinstance(preds, tuple):
        preds = preds[0]
    decoded_preds = tokenizer.batch_decode(preds, skip_special_tokens=True)
    # Replace -100 in the labels as we can't decode them.
    labels = np.where(labels != -100, labels, tokenizer.pad_token_id)
    decoded_labels = tokenizer.batch_decode(labels, skip_special_tokens=True)

    # Some simple post-processing
    decoded_preds, decoded_labels = postprocess_text(decoded_preds, decoded_labels)

    result = metric.compute(predictions=decoded_preds, references=decoded_labels, use_stemmer=True)
    result = {k: round(v * 100, 4) for k, v in result.items()}
    prediction_lens = [np.count_nonzero(pred != tokenizer.pad_token_id) for pred in preds]
    result["gen_len"] = np.mean(prediction_lens)
    return result


# Before we can start training is to create a `DataCollator` that will take care of padding our inputs and labels. We will use the `DataCollatorForSeq2Seq` from the 🤗 Transformers library. 

# In[54]:


from transformers import DataCollatorForSeq2Seq

# we want to ignore tokenizer pad token in the loss
label_pad_token_id = -100
# Data collator
data_collator = DataCollatorForSeq2Seq(
    tokenizer,
    model=model,
    label_pad_token_id=label_pad_token_id,
    pad_to_multiple_of=8
)


# The last step is to define the hyperparameters (`TrainingArguments`) we want to use for our training. We are leveraging the [Hugging Face Hub](https://huggingface.co/models) integration of the `Trainer` to automatically push our checkpoints, logs and metrics during training into a repository.

# In[62]:


# from huggingface_hub import HfFolder ## depcreated
from transformers import Seq2SeqTrainer, Seq2SeqTrainingArguments


RESULTS_DIR = os.getenv('WORK_DIR', '/teamspace/studios/this_studio/data')
assert os.path.exists(RESULTS_DIR), f"Results directory {RESULTS_DIR} does not exist"

# Hugging Face repository id
output_dir = f"{os.path.join(RESULTS_DIR, MODEL_ID.split('/')[1])}-scan-summarization"

repository_id = f"{hf_username}/{MODEL_ID.split('/')[1]}-scan-summarization"

# Define training args
training_args = Seq2SeqTrainingArguments(
    output_dir=output_dir,
    per_device_train_batch_size=4,
    per_device_eval_batch_size=4,
    predict_with_generate=True,
    fp16=False, # Overflows with fp16
    learning_rate=5e-5,
    num_train_epochs=10,
    # logging & evaluation strategies
    logging_strategy="steps",
    logging_steps=500,
    eval_strategy="epoch",
    save_strategy="epoch",
    save_total_limit=2,
    load_best_model_at_end=True,
    # metric_for_best_model="overall_f1",
    # push to hub parameters
    report_to="tensorboard",
    push_to_hub=False,
    hub_strategy="every_save",
    hub_model_id=repository_id,
    hub_token=hf_token,
)

# Create Trainer instance
trainer = Seq2SeqTrainer(
    model=model,
    args=training_args,
    data_collator=data_collator,
    train_dataset=tokenized_dataset["train"],
    eval_dataset=tokenized_dataset["test"],
    compute_metrics=compute_metrics,
)


# In[63]:


print(f"Encoder embeddings shape: {model.encoder.embed_tokens.weight.shape}")
print(f"Decoder embeddings shape: {model.decoder.embed_tokens.weight.shape}")
print(f"Are weights initialized: {model.encoder.embed_tokens.weight.sum().item() != 0 and model.decoder.embed_tokens.weight.sum().item() != 0}")


# We can start our training by using the `train` method of the `Trainer`.
# 
# __NOTE__: Add `DVCLiveCallback` to track updates on DVC.

# In[64]:


# from dvclive.huggingface import DVCLiveCallback

# trainer.add_callback(DVCLiveCallback(save_dvc_exp=True))


# In[ ]:


# Start training
trainer.train()


# ![flan-t5-tensorboard](../assets/flan-t5-tensorboard.png)

# Nice, we have trained our model. 🎉 Lets run evaluate the best model again on the test set.
# 

# In[59]:


trainer.evaluate()


# The best score we achieved is an `rouge1` score of `47.23`. 
# 
# Lets save our results and tokenizer to the Hugging Face Hub and create a model card. 

# In[ ]:


# Save our tokenizer and create model card
tokenizer.save_pretrained(repository_id)
trainer.create_model_card()
# Push the results to the hub
trainer.push_to_hub()


# ## 4. Run Inference
# 
# Now we have a trained model, we can use it to run inference. We will use the `pipeline` API from transformers and a `test` example from our dataset.

# %% [markdown]

# %% [markdown]

# Load model directly from saved checkpoint

# %% 

from random import randrange

# Select a random test sample

# Select a random test sample
sample = dataset['test'][randrange(len(dataset["test"]))]
print(f"prompt: \n{sample['prompt']}\n---------------")

# Prepare input
input_text = "summarize: " + sample["prompt"]
inputs = tokenizer(input_text, return_tensors="pt", max_length=max_source_length, truncation=True)

# %% [markdown]

# Move inputs to GPU if available

# %%

if torch.cuda.is_available():
    inputs = {k: v.to("cuda") for k, v in inputs.items()}
    model.to("cuda")
    
# %%
    
# Generate Summary
with torch.no_grad():
    # Use model.module.generate() if DataParallel was used, otherwise model.generate()
    generate_fn = model.module.generate if isinstance(model, torch.nn.DataParallel) else model.generate
    outputs = generate_fn(
        **inputs,
        max_length=max_target_length,
        num_beams=4,
        length_penalty=2.6,
        # temperature=1.0,
        # top_k=50,
        # top_p=0.95,
        early_stopping=True
    )
    
# Decode and print results
predicted_summary = tokenizer.decode(outputs[0], skip_special_tokens=True)
print(f"Generated summary:\n{predicted_summary}")
print(f"\nReference summary:\n{sample[SUMMARY_COLUMN]}")

# %%

# Get a timestamp (YYYYMMDD_HH:MM)
from datetime import datetime
timestamp = datetime.now().strftime("%Y%m%d_%H%M")

# %% [markdown]

# Saving reference and generated summary to files

# %%

with open(f"{repository_id}/{timestamp}_reference_summary.txt", "w") as f:
    f.write(sample[SUMMARY_COLUMN])
    
with open(f"{repository_id}/{timestamp}_generated_summary.txt", "w") as f:
    f.write(predicted_summary)


# In[ ]:
# from transformers import pipeline
# from random import randrange        

# # Determine device
# device_id = 1 if torch.cuda.is_available() else -1 # Default use GPU #1

# # load model and tokenizer from huggingface hub with pipeline
# try:
#     generator = pipeline("summarization", 
#                           model=repository_id, 
#                           device=device_id)
# except Exception as e:
#     print(f"Summarization pipeline failed: {e}")
#     print("Falling back to text2text-generation pipeline")
#     generator = pipeline("text-generation", 
#                           model=repository_id, 
#                           device=device_id,
#                           temperatur=1.0,
#                           top_k=50,
#                           top_p=0.95)

# # select a random test sample
# sample = dataset['test'][randrange(len(dataset["test"]))]
# print(f"prompt: \n{sample['prompt']}\n---------------")

# # summarize dialogue
# res = generator(sample["prompt"])

# print(f"flan-t5-base summary:\n{res[0]['generated_text']}")

# with open(f"{repository_id}/{timestamp}_pipeline_reference_summary.txt", "w") as f:
#     f.write(sample["summary"])
    
# with open(f"{repository_id}/{timestamp}_pipeline_generated_summary.txt", "w") as f:
#     f.write(res[0]['generated_text'])