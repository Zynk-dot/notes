import time
import os
import sys
import warnings
from transformers import pipeline, logging 

logging.set_verbosity_error()  

summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

TOKEN_LIMIT = 1024

def summarize_text_dynamic(input_text, scaling_factor=0.2, buffer_tokens=20):
    word_count = len(input_text.split())

    max_length = int(word_count * scaling_factor)  
    min_length = int(max_length * 0.6)  

    if max_length > word_count:
        max_length = word_count - 1  

    if max_length < 50:
        max_length = 50
        min_length = 20

    max_length = min(max_length, TOKEN_LIMIT)

    summary = summarizer(
        input_text, 
        max_length=max_length + buffer_tokens,  
        min_length=min_length, 
        do_sample=False, 
        early_stopping=True,  
    )

    complete_summary = summary[0]['summary_text'].strip()

    if complete_summary[-1] not in ".!?":
        complete_summary = summarize_text_dynamic(input_text, scaling_factor, buffer_tokens + 10)

    return complete_summary

def display_summary(summary_text):
    formatted_summary = summary_text.replace("\n", " ").strip()  
    return formatted_summary

def booting_animation():
    for _ in range(3):
        sys.stdout.write("\rAI Booting .  ")
        sys.stdout.flush()
        time.sleep(0.5)
        sys.stdout.write("\rAI Booting .. ")
        sys.stdout.flush()
        time.sleep(0.5)
        sys.stdout.write("\rAI Booting ...")
        sys.stdout.flush()
        time.sleep(0.5)
    sys.stdout.write("\r                 \r")  

def break_input_into_chunks(input_text):
    words = input_text.split()
    chunks = []
    
    for i in range(0, len(words), TOKEN_LIMIT):
        chunk = " ".join(words[i:i+TOKEN_LIMIT])
        chunks.append(chunk)
    
    return chunks

def main():
    booting_animation()

    print("Enter the paragraph or passage you'd like summarized (type --done to finish):\n")

    input_text = ""
    while True:
        line = input()
        if line.strip() == "--done":
            break
        input_text += line + "\n"

    os.system('clear')

    input_chunks = break_input_into_chunks(input_text)

    start_time = time.time()

    word_count = len(input_text.split())
    time_taken_estimation = word_count * 0.05  

    print(f"Estimated Time to Summarize: ~{time_taken_estimation:.2f} seconds\n")

    summary_result = ""
    for chunk in input_chunks:
        summary_result += summarize_text_dynamic(chunk) + " "

    time_taken = time.time() - start_time

    print("\n===================== SUMMARY =====================\n")
    print(display_summary(summary_result.strip()))  
    print("\n====================================================")n
    print(f"\nActual Time Taken: {time_taken:.2f} seconds")

if __name__ == "__main__":
    main()