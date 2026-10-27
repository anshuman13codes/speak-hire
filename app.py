from flask import Flask, render_template, request, jsonify
from groq import Groq
import os
app = Flask(__name__)
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# WORKING MODEL FOR FREE ACCOUNTS - OCT 2026
MODEL = "openai/gpt-oss-20b"

def get_ai_questions(role):
    try:
        prompt = f"Generate 5 tough technical interview questions for: {role}. Only numbered list."
        completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=MODEL,
        )
        text = completion.choices[0].message.content
        lines = [l.strip() for l in text.split('\n') if len(l.strip()) > 10]
        clean = []
        for l in lines:
            if l and l[0].isdigit():
                clean.append(l.split('.',1)[-1].strip() if '.' in l else l)
            else:
                clean.append(l)
        return clean[:5]
    except Exception as e:
        print("AI Error:", str(e))
        return [f"AI Error: {e}", "Try again", "Check internet", "Q4", "Q5"]

def evaluate_answer(question, answer):
    try:
        prompt = f"Q: {question}\nAns: {answer}\nGive short feedback and score /10."
        completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=MODEL,
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error: {e}"

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        role = request.form.get("role", "")
        questions = get_ai_questions(role)
        return render_template("interview.html", role=role, questions=questions)
    return render_template("index.html")

@app.route("/evaluate", methods=["POST"])
def evaluate():
    data = request.get_json()
    result = evaluate_answer(data['question'], data['answer'])
    return jsonify({"feedback": result})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))