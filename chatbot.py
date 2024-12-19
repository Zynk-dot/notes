import os
import time
import pickle
from transformers import pipeline, AutoTokenizer, AutoModelForQuestionAnswering
import spacy

# Load SpaCy model for text preprocessing and chunking
def load_spacy_model(model_name="en_core_web_sm"):
    try:
        nlp = spacy.load(model_name)
    except OSError:
        print(f"Model '{model_name}' not found. Installing it now...")
        os.system(f"python -m spacy download {model_name}")
        nlp = spacy.load(model_name)
    return nlp

nlp = load_spacy_model()

# Load a pre-trained model for question answering
MODEL_NAME = "deepset/roberta-large-squad2"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForQuestionAnswering.from_pretrained(MODEL_NAME)
qa_pipeline = pipeline("question-answering", model=model, tokenizer=tokenizer)

# Cache file for passage chunks
CACHE_FILE = "passage_cache.pkl"

# Chunking function to handle large passages
def split_into_chunks(text, word_limit=250):
    """
    Splits the text into smaller chunks, ensuring splits occur at sentence boundaries.
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

def preprocess_passage(passage):
    """
    Preprocesses and caches the passage for reuse.
    """
    chunks = split_into_chunks(passage, word_limit=250)
    with open(CACHE_FILE, "wb") as f:
        pickle.dump(chunks, f)
    print(f"Passage preprocessed into {len(chunks)} chunks and cached.")

def load_cached_chunks():
    """
    Loads cached passage chunks from disk.
    """
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "rb") as f:
            return pickle.load(f)
    return []

def clear_cache():
    """
    Clears the cached passage chunks from disk.
    """
    if os.path.exists(CACHE_FILE):
        os.remove(CACHE_FILE)
        print("Cache cleared.")

def rank_chunks_by_relevance(chunks, question):
    """
    Ranks chunks by their relevance to the question using simple keyword matching.
    """
    question_tokens = set(question.lower().split())
    ranked_chunks = []

    for chunk in chunks:
        chunk_tokens = set(chunk.lower().split())
        common_tokens = question_tokens.intersection(chunk_tokens)
        score = len(common_tokens)
        ranked_chunks.append((chunk, score))

    ranked_chunks.sort(key=lambda x: x[1], reverse=True)
    return [chunk for chunk, _ in ranked_chunks if _ > 0]

def answer_question(question, extended_response=False):
    """
    Answers a question based on the cached passage chunks.
    """
    chunks = load_cached_chunks()

    if not chunks:
        print("No passage cached. Please provide a passage first.")
        return None

    # Rank chunks by relevance
    relevant_chunks = rank_chunks_by_relevance(chunks, question)

    if not relevant_chunks:
        print("No relevant chunks found for the question.")
        return None

    answers = []

    for i, chunk in enumerate(relevant_chunks[:5]):  # Process top 5 relevant chunks
        print(f"Processing relevant chunk {i+1}/{len(relevant_chunks)}...")
        try:
            answer = qa_pipeline({"question": question, "context": chunk})
            answers.append(answer)
        except Exception as e:
            print(f"Error processing chunk {i+1}: {e}")

    # Select the best answer based on score
    best_answer = max(answers, key=lambda x: x['score']) if answers else None

    if best_answer and extended_response:
        # Generate a longer response based on context
        context = max(relevant_chunks, key=lambda c: best_answer['answer'] in c)
        extended_response = qa_pipeline({"question": f"Explain in detail: {question}", "context": context})
        best_answer['answer'] = extended_response['answer']

    return best_answer

def main():
    """
    Main function to take passage and questions, and provide answers interactively.
    """
    print("Enter the passage (type --done to finish):\n")
    passage = ""
    while True:
        line = input()
        if line.strip() == "--done":
            break
        passage += line + "\n"

    if passage.strip():
        # Preprocess and cache the passage
        preprocess_passage(passage)

    while True:
        print("\nEnter your question (type --exit to end, type --extend for detailed response):\n")
        question = input().strip()

        if question.lower() == "--exit":
            clear_cache()
            print("Exiting. Goodbye!")
            break

        if question.lower() == "--extend":
            print("Extended response mode activated. Enter your question:\n")
            question = input().strip()
            extended_response = True
        else:
            extended_response = False

        if not question:
            print("No question provided. Please try again.")
            continue

        start_time = time.time()
        answer = answer_question(question, extended_response=extended_response)

        if answer:
            print("\n===================== ANSWER =====================")
            print(f"Answer: {answer['answer']}")
            print(f"Score: {answer['score']:.2f}")
            print("=================================================")
        else:
            print("No answer could be found.")

        print(f"\nTime Taken: {time.time() - start_time:.2f} seconds")

if __name__ == "__main__":
    main()
