import math
import time
import os
import sys
import re
from collections import defaultdict, Counter
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from transformers import pipeline, logging
import spacy

# Suppress warnings
logging.set_verbosity_error()

# Load SpaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except:
    os.system("python -m spacy download en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

# Initialize Summarization Pipeline
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# Constants
WORD_LIMIT = 250
MIN_WORD_COUNT_FOR_SUMMARY = 20

def split_into_chunks(text, word_limit=WORD_LIMIT):
    """
    Splits text into smaller chunks of up to `word_limit` words,
    ensuring splits occur at sentence boundaries.
    """
    doc = nlp(text)
    chunks = []
    current_chunk = []
    current_word_count = 0

    for sentence in doc.sents:
        sentence_word_count = len(sentence.text.split())
        if current_word_count + sentence_word_count > word_limit:
            chunks.append(" ".join(current_chunk))
            current_chunk = []
            current_word_count = 0

        current_chunk.append(sentence.text)
        current_word_count += sentence_word_count

    if current_chunk:
        chunks.append(" ".join(current_chunk))  # Add the last chunk

    return chunks

def summarize_text_dynamic(input_text, scaling_factor=0.3):
    """
    Summarizes input text dynamically with scaling based on chunk size.
    """
    word_count = len(input_text.split())
    max_length = min(int(word_count * scaling_factor), 512)
    min_length = int(max_length * 0.6)

    summary = summarizer(
        input_text, 
        max_length=max_length, 
        min_length=min_length, 
        do_sample=False
    )
    return summary[0]["summary_text"].strip()

def generate_bullets(summary_text):
    """
    Generates bullet points from a summarized text.
    """
    bullets = []
    doc = nlp(summary_text)
    sentences = [sent.text.strip() for sent in doc.sents]

    for sentence in sentences:
        bullets.append(f"  • {sentence.capitalize()}")

    return bullets

def normalize_themes(themes):
    """
    Normalize themes by lemmatizing and converting to lowercase.
    """
    lemmatized_themes = []
    for theme in themes:
        doc = nlp(theme)
        lemma = " ".join([token.lemma_ for token in doc])
        lemmatized_themes.append(lemma.lower())
    return lemmatized_themes

def merge_similar_themes(themes, threshold=0.7):
    """
    Merge similar themes using cosine similarity.
    Themes with similarity above the threshold are combined.
    """
    vectorizer = CountVectorizer().fit_transform(themes)
    vectors = vectorizer.toarray()
    cosine_matrix = cosine_similarity(vectors)

    merged_themes = {}
    used = set()

    for i, theme1 in enumerate(themes):
        if i in used:
            continue
        group = [theme1]
        for j, theme2 in enumerate(themes):
            if i != j and j not in used and cosine_matrix[i][j] > threshold:
                group.append(theme2)
                used.add(j)
        used.add(i)
        merged_themes[" & ".join(group)] = group[0]  # Combine similar themes

    return merged_themes

def extract_themes_from_text(text):
    """
    Extracts key themes (topics) from the text dynamically using keyword analysis.
    """
    doc = nlp(text)
    
    # Extract nouns and proper nouns for theme detection
    candidates = [chunk.text.lower() for chunk in doc.noun_chunks]
    stopwords = {"which", "that", "these", "those", "this", "it", "its"}  # Add more if needed
    filtered_candidates = [word for word in candidates if word not in stopwords]
    
    # Rank themes by frequency
    theme_counts = Counter(filtered_candidates)
    top_themes = [item[0] for item in theme_counts.most_common(7)]  # Limit to top 7 themes
    
    # Capitalize themes for output
    return [theme.capitalize() for theme in top_themes]

def group_bullets_by_themes(bullets, themes):
    """
    Groups bullet points under normalized and merged themes.
    """
    # Normalize themes
    normalized_themes = normalize_themes(themes)
    merged_theme_map = merge_similar_themes(normalized_themes)

    # Map bullets to merged themes
    theme_groups = defaultdict(list)
    for bullet in bullets:
        assigned = False
        for raw_theme, normalized_theme in merged_theme_map.items():
            if normalized_theme in bullet.lower():
                theme_groups[raw_theme].append(bullet)
                assigned = True
                break
        if not assigned:
            theme_groups["Miscellaneous"].append(bullet)

    # Format grouped bullets
    grouped_output = []
    for theme, points in theme_groups.items():
        grouped_output.append(f"- {theme.capitalize()}")
        grouped_output.extend(points)
    return grouped_output

def main():
    """
    Main function for summarization workflow.
    """
    print("Enter the paragraph you'd like summarized (type --done to finish):\n")
    input_text = ""
    while True:
        line = input()
        if line.strip() == "--done":
            break
        input_text += line + "\n"

    os.system("cls" if os.name == "nt" else "clear")

    if len(input_text.split()) < MIN_WORD_COUNT_FOR_SUMMARY:
        print("Text is too short to summarize. Please provide a longer input.")
        return

    # Split input into manageable chunks (250 words max per chunk)
    chunks = split_into_chunks(input_text, word_limit=250)
    print(f"\nProcessing {len(chunks)} chunks...\n")

    all_bullets = []  # Store only bullet points
    start_time = time.time()

    for i, chunk in enumerate(chunks):
        print(f"Processing chunk {i+1}/{len(chunks)}...")

        # Summarize the chunk
        summarized_text = summarize_text_dynamic(chunk)

        # Convert summary to bullet points and discard raw summary
        if summarized_text:
            bullets = generate_bullets(summarized_text)
            all_bullets.extend(bullets)

        print(f"Completed chunk {i+1}/{len(chunks)}.\n")

    # Extract themes dynamically
    themes = extract_themes_from_text(input_text)
    print(f"\nDetected Themes: {', '.join(themes)}")

    # Group bullets by detected themes
    grouped_bullets = group_bullets_by_themes(all_bullets, themes)

    # Output the final summary
    print("\n===================== NESTED BULLET SUMMARY =====================\n")
    print("\n".join(grouped_bullets))
    print("\n=================================================================")
    print(f"\nActual Time Taken: {time.time() - start_time:.2f} seconds")

if __name__ == "__main__":
    main()
