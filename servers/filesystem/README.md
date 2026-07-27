# 🗂️ Filesystem Tool Server

A FastAPI-powered server to interact with your filesystem via OpenAPI.

## 🚀 Quickstart

Clone the repo and run the server:

```bash
git clone https://github.com/open-webui/openapi-servers
cd openapi-servers/servers/filesystem
pip install -r requirements.txt

# Optional: configure allowed directories (defaults to ~/tmp)
cp .env.example .env
uvicorn main:app --host 0.0.0.0 --reload
```

## ⚙️ Configuration

Allowed paths are controlled by the `ALLOWED_DIRECTORIES` environment variable (comma-separated). The default is `~/tmp`. Copy `.env.example` to `.env` and edit to taste.

📡 Your Filesystem server will be live at:  
http://localhost:8000/docs

---

Built for plug & play ⚡