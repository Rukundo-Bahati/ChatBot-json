import nltk
from flask import Flask, render_template, request, jsonify
import json
from nltk.tokenize import word_tokenize
from flask_cors import CORS
import random
from typing import Optional


# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Functions to load and save knowledge base
def load_knowledge_base(file_path: str) -> dict:
    with open(file_path, 'r') as file:
        data: dict = json.load(file)
    return data


def save_knowledge_base(file_path: str, data: dict):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=2)


# Function to find the best match for a question using NLTK tokenization
def find_best_match(user_question: str, knowledge_base: dict) -> Optional[str]:
    user_tokens = set(word_tokenize(user_question.lower()))

    best_match = None
    best_match_score = 0

    for q in knowledge_base["questions"]:
        question_tokens = set(word_tokenize(q["question"].lower()))
        score = len(user_tokens.intersection(question_tokens))  # Count common tokens

        if score > best_match_score:
            best_match_score = score
            best_match = q["question"]

    return best_match


# Function to get the answer to a question
def get_answer_for_question(question: str, knowledge_base: dict) -> str:
    for q in knowledge_base["questions"]:
        if q["question"].lower() == question.lower():
            return random.choice(q["answer"])  # Return a random answer if there are multiple
    return "I don't know the answer. Can you teach me?"


# Route to handle chatbot requests
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    # Load the knowledge base
    knowledge_base = load_knowledge_base("knowledge_base.json")

    user_input = request.json.get("question")
    if not user_input:
        return jsonify({"error": "Invalid question input"}), 400

    best_match = find_best_match(user_input, knowledge_base)

    if best_match:
        answer = get_answer_for_question(best_match, knowledge_base)
        return jsonify({"response": answer})
    else:
        return jsonify({"response": "I don't know the answer. Can you teach me?"})


# Route to handle saving new questions/answers
@app.route("/teach", methods=["POST"])
def teach():
    # Load the knowledge base
    knowledge_base = load_knowledge_base("knowledge_base.json")

    user_question = request.json.get("question")
    user_answer = request.json.get("answer")

    if user_question and user_answer:
        knowledge_base["questions"].append({"question": user_question, "answer": [user_answer]})
        save_knowledge_base("knowledge_base.json", knowledge_base)
        return jsonify({"message": "Thank you! I learned a new response."})
    else:
        return jsonify({"error": "Invalid input"}), 400


if __name__ == '__main__':
    app.run(debug=True)
