#!/usr/bin/env python3
"""
Utils: Common configurations for the project
"""

import os
import torch

OUTPUT_DIR = "/work/mupr624/data/vLLM-Lab"
MARKERS_DIR = os.path.join(OUTPUT_DIR, "markers")

ENV_FILE = "/work/mupr624/jupyter_notebooks/.env"

def get_token(token_name: str) -> str:
    """Helper function to load .env tokens."""
    if not os.path.exists(ENV_FILE):
        raise FileNotFoundError(f"Environment file '{ENV_FILE}' not found.")
    
    from dotenv import load_dotenv
    
    load_dotenv(ENV_FILE)
    token = os.getenv(token_name)
    if token is None:
        raise ValueError(f"Token '{token_name}' not found in environment variables.")
    return token

def configure_runtime():
    """Configure the runtime environment for optimal performance with vLLM and PyTorch."""

    # Set allocator/env flags before importing torch/vllm.
    os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")
    os.environ.setdefault("CUDA_VISIBLE_DEVICES", "0")
    os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
    
    # FlashInfer sampler JIT can fail in mixed Python/CUDA setups; force native sampler.
    os.environ.setdefault("VLLM_USE_FLASHINFER_SAMPLER", "0")
    
    # Create output directories if they don't exist
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(MARKERS_DIR, exist_ok=True)
    
    with torch.no_grad():
        torch.cuda.empty_cache()
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}, {torch.cuda.get_device_name(0) if device.type == 'cuda' else 'CPU'}")
    print(f"Total memory: {device}, {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB" if device.type == "cuda" else "N/A ")
    return device
