#!/usr/bin/env python3
"""
Pre-run data collection script for the "arXiv LLM Fine-Tuning Papers Weekly" cron job.

This script queries the arXiv API for recent LLM fine-tuning papers and outputs
the results in a format that gets injected into the AI agent's prompt context.

Usage:
    python scripts/arxiv-fine-tuning-weekly.py
"""

import sys
import os

# Add the scripts directory to path so we can import search_arxiv
scripts_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)))
if scripts_dir not in sys.path:
    sys.path.insert(0, scripts_dir)

from search_arxiv import search_arxiv, format_papers

QUERY = (
    'all:"LLM fine-tuning"'
    '+OR+all:"large language model fine-tuning"'
    '+OR+all:"fine-tuning LLM"'
    '+OR+all:"LoRA fine-tuning"'
    '+OR+all:"instruction tuning"'
    '+OR+all:"RLHF"'
    '+OR+all:"PEFT"'
    '+OR+all:"supervised fine-tuning"'
    '+OR+all:"parameter efficient fine-tuning"'
    '+OR+all:"QLoRA"'
)


def main():
    # Fetch latest papers sorted by submission date (newest first)
    print("=== arXiv LLM Fine-Tuning Papers (Recent) ===")
    print(f"Queried at: {__import__('datetime').datetime.now().isoformat()}")
    print(f"Query: LLM fine-tuning techniques (LoRA, QLoRA, PEFT, SFT, RLHF, instruction tuning)")
    print()

    papers = search_arxiv(QUERY, max_results=20, sort_by='submittedDate', sort_order='descending')

    if not papers:
        print("No papers found from arXiv API.")
        sys.exit(0)

    # Filter to only relevant fine-tuning papers
    relevant_keywords = [
        'lora', 'qlora', 'peft', 'fine-tun', 'instruction tun', 'rlhf',
        'supervised', 'sft', 'dpo', 'grpo', 'ppo', 'reward model',
        'adapter', 'prompt tun', 'prefix tun', 'bitfit', 'ia3',
        'parameter efficien', 'model alignment', 'human feedback',
        'distillation', 'knowledge distil', 'quantiz',
    ]

    filtered = []
    for p in papers:
        combined = (p['title'] + ' ' + p['summary']).lower()
        if any(kw in combined for kw in relevant_keywords):
            filtered.append(p)

    print(f"Found {len(papers)} total, {len(filtered)} fine-tuning relevant")
    print()

    # Output top 15 most relevant for the AI to select from
    print(format_papers(filtered[:15], show_full_abstract=False))

    # Also output JSON for structured processing
    print()
    print("=== JSON DATA ===")
    from search_arxiv import format_json
    print(format_json(filtered[:15]))

    print()
    print("=== END ===")


if __name__ == '__main__':
    main()
