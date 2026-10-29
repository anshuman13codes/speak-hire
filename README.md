# 🎤 Speak-Hire - AI Powered Mock Interview Platform

> Crack your dream job with AI-powered mock interviews.

### ✨ Features

- 🤖 **Real AI Interviewer** - Asks smart questions based on your role
- 🎯 **Role Based** - For Software Engineer, Data Analyst, HR, etc.
- 💬 **Instant Feedback** - AI gives you score & improvement tips
- 🎨 **Clean UI** - Simple, fast, professional design
- ⚡ **Fast** - Powered by Groq LLM
- 🔐 **Google sign-in** - Verified Gmail accounts are required to access the app

### 🛠️ Tech Stack

- **Backend:** Python Flask
- **Authentication:** Google OAuth 2.0 via Authlib
- **AI:** Groq API (Llama 3.3)
- **Frontend:** HTML, CSS, JavaScript
- **Deployment:** Vercel

### 🚀 Deploy to Vercel

1. Select **Add New → Project** in [Vercel](https://vercel.com/new) and import this GitHub repository. Select the branch containing these deployment files. Vercel uses `vercel.json` to deploy the Flask app in `app.py`.
2. Before deploying, open **Project Settings → Environment Variables** in Vercel and add:

   | Name | Value |
   | --- | --- |
   | `GROQ_API_KEY` | Your key from [Groq Console](https://console.groq.com/keys) |
   | `FLASK_SECRET_KEY` | A long, random, persistent secret |
   | `GOOGLE_CLIENT_ID` | Your Google OAuth web client ID |
   | `GOOGLE_CLIENT_SECRET` | Your Google OAuth web client secret |
   | `GOOGLE_REDIRECT_URI` | `https://<your-vercel-domain>/auth/callback` |
   | `COOKIE_SECURE` | `true` |

   Set the variables for the **Production** environment (and Preview too, if you use preview deployments). You can use the project domain shown by Vercel for `GOOGLE_REDIRECT_URI`; if the domain is not assigned yet, deploy once to obtain it, then update the variables and redeploy. Never put real keys in source files or commit `.env`.
3. In Google Cloud Console, add the exact `GOOGLE_REDIRECT_URI` above to the OAuth client's **Authorized redirect URIs**. Save the changes in Google Cloud and redeploy on Vercel so the configured environment variables take effect.
4. The deployed site is reachable on the internet, and visitors must sign in with a verified Gmail account before using it.

The repository includes `.env.example` for local setup only. Vercel does not read that file as its deployment secrets; add `GROQ_API_KEY` and the other values in the Vercel Environment Variables dashboard.

### 🧑‍💻 Run Locally

1. **Clone the repo**

```bash
git clone https://github.com/anshuman13codes/speak-hire.git
cd speak-hire
```

2. **Install dependencies**

```bash
python -m pip install -r requirements.txt
```

3. **Configure Google OAuth**

Create an OAuth 2.0 Client ID in the [Google Cloud Console](https://console.cloud.google.com/apis/credentials), configure the consent screen, and add this authorized redirect URI:

```text
http://localhost:5000/auth/callback
```

Copy `.env.example` to `.env`, then fill in your OAuth values and a persistent Flask secret. The Groq key is required for generating interview questions and feedback:

```dotenv
GROQ_API_KEY=your-groq-api-key
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=http://localhost:5000/auth/callback
FLASK_SECRET_KEY=your-persistent-random-secret
```

Speak-Hire loads `.env` automatically. If Groq reports an invalid key, use **Click here to configure Groq key** in the app, create or replace the key at [Groq Console](https://console.groq.com/keys), update `.env`, and restart Speak-Hire. For production, set `GOOGLE_REDIRECT_URI` to your deployed URL's `/auth/callback` and register the same URL as an authorized redirect URI in Google Cloud. Set `COOKIE_SECURE=true` when serving over HTTPS. Only verified `@gmail.com` accounts can sign in. Never commit `.env` or downloaded OAuth client-secret files.

4. **Start the app**

```bash
python app.py
