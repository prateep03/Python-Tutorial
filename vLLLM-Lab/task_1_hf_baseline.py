#!/usr/bin/env python3
"""
Task 1: Naive HuggingFace Inference - The Baseline for LLM inference using HuggingFace Transformers.
Measure baseline inference speed using raw HuggingFace Transformers without any optimizations.
"""

import os
import time
from utils import (OUTPUT_DIR, 
                   MARKERS_DIR, 
                   configure_runtime)

    
def main() -> None:
    print("=" * 65)
    print("Task 1: Naive HuggingFace Inference - The Baseline")
    print("=" * 65)
    
    device = configure_runtime()
    
    from transformers import AutoModelForCausalLM, AutoTokenizer
    
    model_name = "HuggingFaceTB/SmolLM-135M"
    prompt = "Explain what a large language model is in simple terms"
    
    print(f"\nModel: {os.path.basename(model_name)}")
    print(f"Prompt: \"{prompt}\"")
    print("-" * 65)

    # -- LOAD MODEL --
    print("\nLoading model with HuggingFace transformers")
    model = AutoModelForCausalLM.from_pretrained(model_name).to(device)
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    
    # Set pad token if not set
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
        
    print("Model loaded successfully...")
    
    # -- GENERATE --
    print("\nGenerating with HuggingFace transformers")
    model_inputs = tokenizer(prompt, return_tensors="pt").to(device)
    
    start_time = time.time()
    outputs = model.generate(
        input_ids=model_inputs.input_ids, 
        attention_mask=model_inputs.attention_mask,
        pad_token_id=tokenizer.eos_token_id,
        max_new_tokens=50, 
        temperature=0.7
    )
    end_time = time.time()
    
    # Calculate metrics
    input_tokens = model_inputs["input_ids"].shape[1]
    total_tokens = outputs[0].shape[0] if hasattr(outputs, '__getitem__') else outputs.shape[1]
    generated_tokens = total_tokens - input_tokens
    total_time = end_time - start_time
    tokens_per_second = generated_tokens / total_time
    
    # Decode output
    output_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    # -- RESULTS --
    print("\n--- RESULTS ---")
    print(f"Generated text: {output_text[:200]}...")
    print(f"\nGenrated tokens: {generated_tokens}")
    print(f"Total time: {total_time:.2f} seconds")
    print(f"Tokens per second: {tokens_per_second:.1f} tok/s")
    
    # Save baseline for later comparison
    baseline_file = os.path.join(MARKERS_DIR, "hf_baseline.txt")
    with open(baseline_file, "w") as f:
        f.write(f"tokens_per_second={tokens_per_second:.2f}\n")
        f.write(f"total_time={total_time:.4f}\n")
        f.write(f"generated_tokens={generated_tokens}\n")
        
    # --- KEY INSIGHT ---
    print("\n" + "=" * 65)
    print("KEY INSIGHT:")
    print("- This is a SINGLE-REQUEST performance")
    print("- There is no batching - one request at a time")
    print("- Under load with multiple users, requests would queue up")
    print("- Next: See how vLLM improves this (Task 2)")
    
    # Create marker file
    with open(os.path.join(MARKERS_DIR, "task1_complete.txt"), "w") as f:
        f.write("TASK_1_COMPLETE\n")
        
    print("\nTask 1 Complete!")
    print("Next: uv run --active task_2_vllm_inference.py")
    
    # Clean up
    del model
    del tokenizer
    
    
if __name__ == "__main__":
    main()