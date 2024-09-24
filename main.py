from flask import Flask, render_template, request, jsonify
import json
from difflib import get_close_matches

# Initialize Flask app
app = Flask(__name__)


# Functions to load and save knowledge base
def load_knowledge_base(file_path: str) -> dict:
    with open(file_path, 'r') as file:
        data: dict = json.load(file)
    return data


def save_knowledge_base(file_path: str, data: dict):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=2)


# Function to find the closest match for a question
def find_best_match(user_question: str, questions: list[str]) -> str | None:
    matches: list = get_close_matches(user_question, questions, n=2, cutoff=0.5)
    return matches[0] if matches else None


# Function to get the answer to a question
def get_answer_for_question(question: str, knowledge_base: dict) -> str | None:
    for q in knowledge_base["questions"]:
        if q["question"] == question:
            return q["answer"]


# Route to handle chatbot requests
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    # Load the knowledge base
    knowledge_base: dict = load_knowledge_base("knowledge_base.json")

    user_input = request.json.get("question")
    if not user_input:
        return jsonify({"error": "Invalid question input"}), 400

    best_match: str | None = find_best_match(user_input, [q["question"] for q in knowledge_base["questions"]])

    if best_match:
        answer: str = get_answer_for_question(best_match, knowledge_base)
        return jsonify({"response": answer})
    else:
        return jsonify({"response": "I don't know the answer. Can you teach me?"})


# Route to handle saving new questions/answers
@app.route("/teach", methods=["POST"])
def teach():
    # Load the knowledge base
    knowledge_base: dict = load_knowledge_base("knowledge_base.json")

    user_question = request.json.get("question")
    user_answer = request.json.get("answer")

    if user_question and user_answer:
        knowledge_base["questions"].append({"question": user_question, "answer": user_answer})
        save_knowledge_base("knowledge_base.json", knowledge_base)
        return jsonify({"message": "Thank you! I learned a new response."})
    else:
        return jsonify({"error": "Invalid input"}), 400


if __name__ == '__main__':
    app.run(debug=True)
