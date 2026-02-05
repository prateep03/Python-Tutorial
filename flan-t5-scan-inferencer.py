#!/usr/bin/env python3
"""
Inference script for FLAN-T5 Scan Summarization Model

This script loads a fine-tuned FLAN-T5 model from a checkpoint and runs inference
on sample scan texts to generate summaries.

Usage:
    # Run with sample inputs using checkpoint-4290
    python flan-t5-scan-inference.py --checkpoint checkpoint-4290

    # Run with checkpoint-3861
    python flan-t5-scan-inference.py --checkpoint checkpoint-3861

    # Provide custom input
    python flan-t5-scan-inference.py --checkpoint checkpoint-4290 --input "Your document text here"

    # Interactive mode
    python flan-t5-scan-inference.py --checkpoint checkpoint-4290 --interactive

"""

import os
import sys
import argparse
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from datetime import datetime
from typing import Optional, List, Dict
import json


class ScanSummarizer:
    """Wrapper class for FLAN-T5 scan summarization inference."""
    
    def __init__(
        self,
        checkpoint_path: str,
        device: Optional[str] = None,
        max_source_length: int = 512,
        max_target_length: int = 128
    ):
        """
        Initialize the summarizer with a model checkpoint.
        
        Args:
            checkpoint_path: Path to the model checkpoint directory
            device: Device to run inference on ('cuda' or 'cpu'). Auto-detected if None.
            max_source_length: Maximum length for input text
            max_target_length: Maximum length for generated summary
        """
        self.checkpoint_path = checkpoint_path
        self.max_source_length = max_source_length
        self.max_target_length = max_target_length
        
        # Auto-detect device if not specified
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device
            
        print(f"Loading model from: {checkpoint_path}")
        print(f"Using device: {self.device}")
        
        if self.device == "cuda":
            torch.cuda.empty_cache()
    
            # Reset peak memory stats
            torch.cuda.reset_peak_memory_stats()
            torch.cuda.reset_accumulated_memory_stats()
        
        # Load tokenizer and model
        self._load_model()
        
    def _load_model(self):
        """Load the tokenizer and model from checkpoint."""
        try:
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.checkpoint_path,
                trust_remote_code=True
            )
            
            # Load model
            self.model = AutoModelForSeq2SeqLM.from_pretrained(
                self.checkpoint_path,
                trust_remote_code=True
            )
            
            # Move model to device
            self.model.to(self.device)
            self.model.eval()  # Set to evaluation mode
            
            print(f"Model loaded successfully!")
            print(f"Model type: {self.model.config.model_type}")
            print(f"Vocab size: {self.tokenizer.vocab_size}")
            
            if self.device == "cuda":
                print(f"GPU: {torch.cuda.get_device_name(0)}")
                print(f"GPU memory allocated: {torch.cuda.memory_allocated(0) / 1024**3:.2f} GB")
                
        except Exception as e:
            print(f"Error loading model: {e}")
            raise Exception(f"Failed to load model from checkpoint: {self.checkpoint_path}") from e
        
    def _format_summary(self, summary: str) -> str:
        """
        Format the summary text to match the expected output format.
        
        The format should be:
        RECOMMENDED SETTINGS: 
        
        1. Setting Name
        Reasoning: ...
        
        2. Setting Name
        Reasoning: ...
        
        Args:
            summary: Raw summary text from model
            
        Returns:
            Formatted summary text
        """
        import re
        
        raw_text = summary.replace("RECOMMENDED SETTINGS:", "").strip()
        
        # Split by numbered points (1., 2., etc)
        parts = re.split(r'\s*(\d+\.)\s*', raw_text)
        
        formatted = "RECOMMENDED SETTINGS:\n\n"
        
        # parts look like: ['', '1.', 'text..', '2.', 'text...', ...]
        for i in range(1, len(parts), 2):
            number = parts[i]
            content = parts[i + 1].strip()
            
            # Split setting and reasoning
            if "Reasoning:" in content:
                setting, reasoning = content.split("Reasoning:", 1)
                setting = setting.strip()
                reasoning = reasoning.strip()
            else:
                setting = content
                reasoning = ""
                
            formatted += f"{number} {setting}\n"
            if reasoning:
                formatted += f"Reasoning: {reasoning}\n\n"
            else:
                formatted += "\n"
                
        return formatted.strip()
                   
    def summarize(
        self,
        text: str,
        num_beams: int = 4,
        length_penalty: float = 2.0,
        early_stopping: bool = True,
        temperature: Optional[float] = None,
        top_k: Optional[int] = None,
        top_p: Optional[float] = None,
        do_sample: bool = False
    ) -> str:
        """
        Generate a summary for the given text.
        
        Args:
            text: Input document text to summarize
            num_beams: Number of beams for beam search
            length_penalty: Length penalty for beam search
            early_stopping: Whether to stop generation early
            temperature: Sampling temperature (if do_sample=True)
            top_k: Top-k sampling parameter (if do_sample=True)
            top_p: Top-p (nucleus) sampling parameter (if do_sample=True)
            do_sample: Whether to use sampling instead of beam search
            
        Returns:
            Generated summary text
        """
        # Prepare input with prompt template
        prompt = f"summarize the following document scan text:\n\n{text}\n\nSummary:"
        
        # Tokenize input
        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            max_length=self.max_source_length,
            truncation=True,
            padding=True
        )
        
        # Move inputs to device
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        # Prepare generation kwargs
        gen_kwargs = {
            "max_length": self.max_target_length,
            "num_beams": num_beams,
            "length_penalty": length_penalty,
            "early_stopping": early_stopping,
            "do_sample": do_sample
        }
        
        # Add sampling parameters if using sampling
        if do_sample:
            if temperature is not None:
                gen_kwargs["temperature"] = temperature
            if top_k is not None:
                gen_kwargs["top_k"] = top_k
            if top_p is not None:
                gen_kwargs["top_p"] = top_p
        
        # Generate summary
        with torch.no_grad():
            outputs = self.model.generate(**inputs, **gen_kwargs)
        
        # Decode and return summary
        summary = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return self._format_summary(summary)
    
    def batch_summarize(
        self,
        texts: List[str],
        batch_size: int = 4,
        **kwargs
    ) -> List[str]:
        """
        Generate summaries for multiple texts in batches.
        
        Args:
            texts: List of input texts to summarize
            batch_size: Number of texts to process at once
            **kwargs: Additional arguments passed to summarize()
            
        Returns:
            List of generated summaries
        """
        summaries = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            print(f"Processing batch {i // batch_size + 1}/{(len(texts) + batch_size - 1) // batch_size}")
            
            for text in batch:
                summary = self.summarize(text, **kwargs)
                summaries.append(summary)
        
        return summaries


def get_sample_inputs() -> List[Dict[str, str]]:
    """Return a list of sample document scan texts for testing."""
    return [
        {
            "title": "Finance",
            "text": """I want to generate print recommendations for a user in the finance/trade industry who prints the 
            following documents with their respective job sizes and job frequencies:

            DocumentType: Reports, JobSize: 21-50 pages, JobFrequency: Occasionally.
            DocumentType: Periodicals, JobSize: 50+ pages, JobFrequency: Several times a day (10–100/day)."""
        },
        {
            "title": "Education",
            "text": """I want to generate print recommendations for a user in the education industry who prints the 
            following documents with their respective job sizes and job frequencies:

            DocumentType: Reports, JobSize: 1-5 pages, JobFrequency: Rarely."""
        },
        {
            "title": "Government Agency",
            "text": """I want to generate print recommendations for a user in the government agency industry who prints the 
            following documents with their respective job sizes and job frequencies:

            DocumentType: Reports, JobSize: 21-50 pages, JobFrequency: Rarely."""
        },
        {
            "title": "Food/Hospitality",
            "text": """I want to generate print recommendations for a user in the food/hospitality industry who prints the 
            following documents with their respective job sizes and job frequencies:

            DocumentType: Menus, JobSize: 6-20 pages, JobFrequency: Few times a week (<10/week)."""
        },
        {
            "title": "Manufacturing",
            "text": """I want to generate print recommendations for a user in the manufacturing industry who prints the 
            following documents with their respective job sizes and job frequencies:

            DocumentType: Reports, JobSize: 50+ pages, JobFrequency: Rarely."""
        }
    ]


def save_results(
    input_text: str,
    summary: str,
    output_dir: str,
    checkpoint_name: str
):
    """Save inference results to files."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Save input
    input_file = os.path.join(output_dir, f"{timestamp}_{checkpoint_name}_input.txt")
    with open(input_file, "w") as f:
        f.write(input_text)
    
    # Save summary
    summary_file = os.path.join(output_dir, f"{timestamp}_{checkpoint_name}_summary.txt")
    with open(summary_file, "w") as f:
        f.write(summary)
    
    # Save metadata
    metadata = {
        "timestamp": timestamp,
        "checkpoint": checkpoint_name,
        "input_length": len(input_text),
        "summary_length": len(summary)
    }
    metadata_file = os.path.join(output_dir, f"{timestamp}_{checkpoint_name}_metadata.json")
    with open(metadata_file, "w") as f:
        json.dump(metadata, f, indent=2)
    
    print(f"\nResults saved to: {output_dir}")
    print(f"  - Input: {input_file}")
    print(f"  - Summary: {summary_file}")
    print(f"  - Metadata: {metadata_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Run inference with fine-tuned FLAN-T5 scan summarization model"
    )
    
    parser.add_argument(
        "--checkpoint",
        type=str,
        default="checkpoint-4290",
        help="Checkpoint directory name (e.g., checkpoint-4290)"
    )
    
    parser.add_argument(
        "--base-path",
        type=str,
        default="/teamspace/studios/this_studio/data/flan-t5-large-scan-summarization",
        help="Base path to the model directory"
    )
    
    parser.add_argument(
        "--input",
        type=str,
        help="Input text to summarize (if not provided, will use sample inputs)"
    )
    
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Run in interactive mode"
    )
    
    parser.add_argument(
        "--output-dir",
        type=str,
        default="./inference_results",
        help="Directory to save inference results"
    )
    
    parser.add_argument(
        "--num-beams",
        type=int,
        default=4,
        help="Number of beams for beam search"
    )
    
    parser.add_argument(
        "--length-penalty",
        type=float,
        default=2.0,
        help="Length penalty for beam search"
    )
    
    parser.add_argument(
        "--device",
        type=str,
        choices=["cuda", "cpu", "auto"],
        default="auto",
        help="Device to run inference on"
    )
    
    parser.add_argument(
        "--max-source-length",
        type=int,
        default=512,
        help="Maximum length for input text"
    )
    
    parser.add_argument(
        "--max-target-length",
        type=int,
        default=128,
        help="Maximum length for generated summary"
    )
    
    args = parser.parse_args()
    
    # Construct full checkpoint path
    checkpoint_path = os.path.join(args.base_path, args.checkpoint)
    
    if not os.path.exists(checkpoint_path):
        print(f"Error: Checkpoint path does not exist: {checkpoint_path}")
        sys.exit(1)
    
    # Set device
    device = None if args.device == "auto" else args.device
    
    # Initialize summarizer
    print("=" * 80)
    print("FLAN-T5 Scan Summarization - Inference")
    print("=" * 80)
    
    summarizer = ScanSummarizer(
        checkpoint_path=checkpoint_path,
        device=device,
        max_source_length=args.max_source_length,
        max_target_length=args.max_target_length
    )
    
    print("\n" + "=" * 80)
    
    # Interactive mode
    if args.interactive:
        print("Interactive Mode - Enter 'quit' or 'exit' to stop")
        print("=" * 80)
        
        while True:
            print("\nEnter document text to summarize (or 'quit' to exit):")
            text = input("> ").strip()
            
            if text.lower() in ['quit', 'exit', 'q']:
                print("Exiting...")
                break
            
            if not text:
                print("Please enter some text.")
                continue
            
            print("\nGenerating summary...")
            summary = summarizer.summarize(
                text,
                num_beams=args.num_beams,
                length_penalty=args.length_penalty
            )
            
            print("\n" + "-" * 80)
            print("INPUT:")
            print("-" * 80)
            print(text)
            print("\n" + "-" * 80)
            print("SUMMARY:")
            print("-" * 80)
            print(summary)
            print("-" * 80)
            
            # Ask if user wants to save
            save = input("\nSave results? (y/n): ").strip().lower()
            if save == 'y':
                save_results(text, summary, args.output_dir, args.checkpoint)
    
    # Single input mode
    elif args.input:
        print(f"Running inference on provided input...")
        print("=" * 80)
        
        summary = summarizer.summarize(
            args.input,
            num_beams=args.num_beams,
            length_penalty=args.length_penalty
        )
        
        print("\n" + "-" * 80)
        print("INPUT:")
        print("-" * 80)
        print(args.input)
        print("\n" + "-" * 80)
        print("SUMMARY:")
        print("-" * 80)
        print(summary)
        print("-" * 80)
        
        # Save results
        save_results(args.input, summary, args.output_dir, args.checkpoint)
    
    # Sample inputs mode
    else:
        print("Running inference on sample inputs...")
        print("=" * 80)
        
        samples = get_sample_inputs()
        
        for i, sample in enumerate(samples, 1):
            print(f"\n{'=' * 80}")
            print(f"SAMPLE {i}/{len(samples)}: {sample['title']}")
            print("=" * 80)
            
            summary = summarizer.summarize(
                sample['text'],
                num_beams=args.num_beams,
                length_penalty=args.length_penalty,
                do_sample=True
            )
            
            print("\n" + "-" * 80)
            print("INPUT:")
            print("-" * 80)
            print(sample['text'])
            print("\n" + "-" * 80)
            print("SUMMARY:")
            print("-" * 80)
            print(summary)
            print("-" * 80)
            
            # Save results
            save_results(
                sample['text'],
                summary,
                os.path.join(args.output_dir, f"sample_{i}"),
                args.checkpoint
            )
        
        print(f"\n{'=' * 80}")
        print(f"Completed inference on {len(samples)} samples")
        print("=" * 80)


if __name__ == "__main__":
    main()