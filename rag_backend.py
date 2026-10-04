
import os
import re

KNOWLEDGE_BASE_FOLDER = "knowledge_base"


def load_knowledge_documents(folder=KNOWLEDGE_BASE_FOLDER):
    documents = []

    if not os.path.exists(folder):
        return documents

    for filename in sorted(os.listdir(folder)):
        if filename.endswith(".md"):
            path = os.path.join(folder, filename)

            with open(path, "r", encoding="utf-8") as f:
                text = f.read()

            documents.append({
                "filename": filename,
                "text": text
            })

    return documents


def create_chunks(documents, chunk_size=500):
    chunks = []

    for document in documents:
        text = document["text"]

        words = text.split()

        for i in range(0, len(words), chunk_size):
            chunk_text = " ".join(words[i:i + chunk_size])

            if chunk_text.strip():
                chunks.append({
                    "filename": document["filename"],
                    "text": chunk_text
                })

    return chunks


def search_business_knowledge(query, top_k=3):
    documents = load_knowledge_documents()
    chunks = create_chunks(documents)

    query_words = set(
        re.findall(r"\b\w+\b", query.lower())
    )

    scored = []

    for chunk in chunks:
        chunk_words = set(
            re.findall(r"\b\w+\b", chunk["text"].lower())
        )

        score = len(query_words.intersection(chunk_words))

        if score > 0:
            scored.append({
                "filename": chunk["filename"],
                "text": chunk["text"],
                "score": score
            })

    scored.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    return scored[:top_k]


def format_knowledge_context(results):
    if not results:
        return "No relevant business knowledge was found."

    parts = []

    for result in results:
        parts.append(
            f"Source: {result['filename']}\n"
            f"{result['text']}"
        )

    return "\n\n".join(parts)
