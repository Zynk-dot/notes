import time
import os
import sys
from transformers import pipeline, logging, BartTokenizer
import re

# Suppress warnings
logging.set_verbosity_error()

# Initialize summarization pipeline and tokenizer
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
tokenizer = BartTokenizer.from_pretrained("facebook/bart-large-cnn")

# Constants
TOKEN_LIMIT = 1024  # Token limit for splitting chunks
MIN_SUMMARY_LENGTH = 50  # Minimum length for summaries
FALLBACK_SUMMARY = "Unable to summarize this section."


def split_into_chunks(text, token_limit=TOKEN_LIMIT):
    """
    Splits text into smaller chunks that fit within the token limit,
    ensuring chunks split at sentence boundaries for coherence.
    """
    sentences = re.split(r'([.!?])\s', text)  # Split into sentences
    chunks = []
    current_chunk = []
    current_length = 0

    for i in range(0, len(sentences), 2):
        sentence = sentences[i]
        if i + 1 < len(sentences):
            sentence += sentences[i + 1]  # Add punctuation back
        sentence_length = len(tokenizer.encode(sentence, truncation=False))

        if current_length + sentence_length > token_limit:
            chunks.append(" ".join(current_chunk).strip())
            current_chunk = []
            current_length = 0

        current_chunk.append(sentence)
        current_length += sentence_length

    if current_chunk:
        chunks.append(" ".join(current_chunk).strip())

    return chunks


def summarize_text_dynamic(input_text, scaling_factor=0.2):
    """
    Dynamically summarize input text with no hard limit on summary length.
    """
    word_count = len(input_text.split())
    max_length = int(word_count * scaling_factor)
    min_length = int(max_length * 0.6)

    # Ensure constraints are feasible
    if min_length >= max_length:
        min_length = max(20, int(max_length * 0.5))  # Set a fallback min_length

    try:
        summary = summarizer(
            input_text,
            max_length=max_length,
            min_length=min_length,
            do_sample=False,
            early_stopping=True,
        )
        return summary[0]['summary_text'].strip()
    except Exception as e:
        print(f"Error during summarization: {str(e)}")
        return FALLBACK_SUMMARY


def display_summary(summary_text):
    """
    Formats and displays the summary.
    """
    formatted_summary = summary_text.replace("\n", " ").strip()
    return formatted_summary


def main():
    """
    Main function for summarization workflow.
    """
    print("Enter the text you'd like summarized (type --done to finish):\n")

    input_text = ""
    while True:
        line = input()
        if line.strip() == "--done":
            break
        input_text += line + "\n"

    os.system('clear')

    try:
        input_chunks = split_into_chunks(input_text, token_limit=TOKEN_LIMIT)
    except Exception as e:
        print(f"Error splitting text into chunks: {str(e)}")
        return

    start_time = time.time()

    print(f"Processing {len(input_chunks)} chunks for summarization.\n")

    intermediate_summaries = []
    for i, chunk in enumerate(input_chunks):
        print(f"Summarizing chunk {i + 1}/{len(input_chunks)}...")
        try:
            summary = summarize_text_dynamic(chunk)
            intermediate_summaries.append(summary)
            del chunk  # Free memory
        except Exception as e:
            print(f"Error summarizing chunk {i + 1}: {str(e)}")
            intermediate_summaries.append(FALLBACK_SUMMARY)

    print("\n===================== SUMMARY =====================\n")
    print(display_summary(" ".join(intermediate_summaries).strip()))
    print("\n====================================================")

    time_taken = time.time() - start_time
    print(f"\nActual Time Taken: {time_taken:.2f} seconds")


if __name__ == "__main__":
    main()
