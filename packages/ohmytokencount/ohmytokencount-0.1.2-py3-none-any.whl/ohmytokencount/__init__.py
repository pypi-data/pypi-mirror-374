"""
Simple token counting tool using tiktoken with GPT-4o tokenizer.
Supports reading from stdin or command line arguments.
"""

import sys
import tiktoken
from typing import Optional


def count_tokens(text: str, model: str = "gpt-4o") -> int:
    """
    Count tokens in the given text using the specified model's tokenizer.

    Args:
        text: The text to count tokens for
        model: The model name to use for tokenization (default: gpt-4o)

    Returns:
        Number of tokens in the text
    """
    encoding = tiktoken.encoding_for_model(model)
    # Allow all special tokens to be encoded properly
    return len(encoding.encode(text, allowed_special="all"))


def get_input_text() -> Optional[str]:
    """
    Get input text from file (command line argument) or stdin.

    Returns:
        The input text, or None if no input provided
    """
    # Check if there are command line arguments
    if len(sys.argv) > 1:
        # Use the first argument as file path
        file_path = sys.argv[1]
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            print(f"Error: File '{file_path}' not found.", file=sys.stderr)
            sys.exit(1)
        except IOError as e:
            print(f"Error reading file '{file_path}': {e}", file=sys.stderr)
            sys.exit(1)

    # Check if stdin has data (not a tty)
    if not sys.stdin.isatty():
        # Read from stdin
        return sys.stdin.read().strip()

    return None


def main():
    """Main function to run the token counting tool."""
    text = get_input_text()

    if text is None:
        print("Usage: python main.py <file_path>", file=sys.stderr)
        print("   or: echo '<text>' | python main.py", file=sys.stderr)
        print("   or: python main.py < file.txt", file=sys.stderr)
        sys.exit(1)

    if not text:
        print("0")
        return

    token_count = count_tokens(text)
    print(token_count)