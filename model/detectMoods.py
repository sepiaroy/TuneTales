import pandas as pd
import requests
from transformers import pipeline

mood_labels = [
    "romantic", "mysterious", "dark", "uplifting", "melancholy", "thrilling", "whimsical", "tragic", "hopeful", "suspenseful", "adventurous", "epic"
]

# classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
classifier = pipeline("zero-shot-classification", model="MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli")

def extract_moods(summary, top_k=3):
    result = classifier(summary, mood_labels)
    return result['labels'][:top_k]  

def search_book_and_get_summary(title, author, max_results=3):
    query = f'intitle:{title}+inauthor:{author}'
    url = "https://www.googleapis.com/books/v1/volumes"
    params = {
        'q': query,
        'maxResults': max_results
    }
    response = requests.get(url, params=params)
    data = response.json()

    if "items" not in data:
        print("No books found.")
        return None

    # Try to find the best match based on exact title and author presence
    for item in data["items"]:
        volume_info = item.get("volumeInfo", {})
        book_title = volume_info.get("title", "").lower()
        authors = [a.lower() for a in volume_info.get("authors", [])]

        if title.lower() in book_title and any(author.lower() in a for a in authors):
            summary = volume_info.get("description") or volume_info.get("subtitle") or "No summary available."
            return summary

    # If no exact match, return first available summary
    first_summary = data["items"][0].get("volumeInfo", {}).get("description", "No summary available.")
    return first_summary

def get_top_moods_for_book(title, author):
    summary = search_book_and_get_summary(title, author)
    if not summary or summary == "No summary available.":
        print("Summary not found or empty.")
        return []

    moods = extract_moods(summary)
    top_3_moods = moods[:3]  # Adjust if your function returns more or less
    return top_3_moods

# Example usage
# book_title = "The Shawshank Redemption"
# book_author = "Stephen King"

# top_moods = get_top_moods_for_book(book_title, book_author)
# print(f"Top 3 moods for '{book_title}' by {book_author}: {top_moods}")