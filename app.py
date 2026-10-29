from functools import wraps
from flask import Flask, render_template, request, jsonify, redirect, session, url_for
from authlib.integrations.base_client.errors import OAuthError
from groq import Groq
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
import os
import secrets

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or secrets.token_hex(32)
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.environ.get("COOKIE_SECURE", "false").lower() == "true",
)

oauth = OAuth(app)
google = oauth.register(
    name="google",
    client_id=os.environ.get("GOOGLE_CLIENT_ID"),
    client_secret=os.environ.get("GOOGLE_CLIENT_SECRET"),
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)

# WORKING MODEL FOR FREE ACCOUNTS - OCT 2026
MODEL = "openai/gpt-oss-20b"
GROQ_KEY_MISSING_MESSAGE = (
    "Groq API key not configured. Please set GROQ_API_KEY in .env file. "
    "Get free key from console.groq.com"
)


class GroqConfigurationError(Exception):
    def __init__(self, message, status_code):
        super().__init__(message)
        self.status_code = status_code


def get_groq_client():
    api_key = os.environ.get("GROQ_API_KEY", "").strip()
    if not api_key:
        raise GroqConfigurationError(GROQ_KEY_MISSING_MESSAGE, 503)
    return Groq(api_key=api_key)


def groq_error_response(error):
    if isinstance(error, GroqConfigurationError):
        message = str(error)
        status_code = error.status_code
        configure = True
    elif getattr(error, "status_code", None) == 401:
        message = "Groq API key is invalid. Please check GROQ_API_KEY in your .env file."
        status_code = 401
        configure = True
    else:
        message = "Could not connect to Groq right now. Please try again."
        status_code = 502
        configure = False
    return message, status_code, configure

def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped


def get_ai_questions(role):
    prompt = f"Generate 5 tough technical interview questions for: {role}. Only numbered list."
    completion = get_groq_client().chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model=MODEL,
    )
    text = completion.choices[0].message.content
    lines = [line.strip() for line in text.split("\n") if len(line.strip()) > 10]
    clean = []
    for line in lines:
        if line and line[0].isdigit():
            clean.append(line.split(".", 1)[-1].strip() if "." in line else line)
        else:
            clean.append(line)
    return clean[:5]

def evaluate_answer(question, answer):
    prompt = f"Q: {question}\nAns: {answer}\nGive short feedback and score /10."
    completion = get_groq_client().chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model=MODEL,
    )
    return completion.choices[0].message.content

@app.route("/", methods=["GET", "POST"])
@login_required
def home():
    if request.method == "POST":
        role = request.form.get("role", "")
        try:
            questions = get_ai_questions(role)
            error = None
            show_configure_button = False
        except Exception as exception:
            error, _, show_configure_button = groq_error_response(exception)
            questions = []
        return render_template(
            "interview.html",
            role=role,
            questions=questions,
            error=error,
            show_configure_button=show_configure_button,
        )
    return render_template("index.html")


@app.route("/configure-groq")
@login_required
def configure_groq():
    return render_template("configure_groq.html", missing_message=GROQ_KEY_MISSING_MESSAGE)


@app.route("/login")
def login():
    return render_template("login.html", error=request.args.get("error"))


@app.route("/auth/google")
def google_login():
    if not os.environ.get("GOOGLE_CLIENT_ID") or not os.environ.get("GOOGLE_CLIENT_SECRET"):
        return redirect(url_for("login", error="Google sign-in is not configured yet."))
    callback_url = os.environ.get("GOOGLE_REDIRECT_URI") or url_for("google_callback", _external=True)
    return google.authorize_redirect(callback_url)


@app.route("/auth/callback")
def google_callback():
    try:
        token = google.authorize_access_token()
    except OAuthError:
        return redirect(url_for("login", error="Google sign-in failed. Please try again."))

    user_info = token.get("userinfo") or {}
    email = user_info.get("email")
    if user_info.get("email_verified") is not True or not isinstance(email, str):
        return redirect(url_for("login", error="Please use a verified Gmail account to continue."))
    email = email.lower()
    if not email.endswith("@gmail.com"):
        return redirect(url_for("login", error="Please use a verified Gmail account to continue."))

    session.clear()
    session["user"] = {
        "email": email,
        "name": user_info.get("name") or email,
        "picture": user_info.get("picture"),
    }
    return redirect(url_for("home"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/evaluate", methods=["POST"])
@login_required
def evaluate():
    data = request.get_json()
    try:
        result = evaluate_answer(data["question"], data["answer"])
        return jsonify({"feedback": result})
    except Exception as exception:
        message, status_code, configure = groq_error_response(exception)
        return jsonify({
            "feedback": message,
            "configure": configure,
            "configure_url": url_for("configure_groq"),
        }), status_code

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))