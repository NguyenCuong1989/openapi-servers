# 🔐 User Info Proxy API

A lightweight FastAPI microservice that forwards an Authorization Bearer token to an internal authentication server and returns user details.

## 🚀 Features

- 🔁 Forwards Bearer tokens to your internal auth endpoint
- 🔒 Built-in error handling

## 📦 Endpoints

### GET /get_session_user_info

Forward your existing Bearer token and get authenticated user details.

📥 Headers:

Authorization: Bearer YOUR_TOKEN

📤 Response:

{
  "id": "user-id",
  "email": "user@example.com",
  "name": "Jane Doe",
  ...
}

## ⚙️ Setup

1. Copy the environment template and edit it:

```bash
cp .env.example .env
```

2. Set your auth backend base URL (or use `.env`):

```
export OPEN_WEBUI_BASE_URL=http://your-open-webui.com
```

3. Run the service:

```
uvicorn main:app --host 0.0.0.0 --reload
```

## 🧩 Environment Variables

| Name                | Description                          | Default              |
|---------------------|--------------------------------------|----------------------|
| OPEN_WEBUI_BASE_URL | Base URL of the internal auth server | http://localhost:3000 |

## 🍿 Example

curl -H "Authorization: Bearer <your_token>" http://localhost:8000/get_session_user_info

## 🧪 Tech Stack

- Python 3.11+
- FastAPI ⚡

---

Made with ❤️ by your backend team.
