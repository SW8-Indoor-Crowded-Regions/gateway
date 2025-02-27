
# 🚀 Gateway
A FastAPI Gateway connecting the frontend with microservices.

---

## 📦 Installation

### ✅ **Prerequisites**
- Ensure you have **Python 3.11** installed.

### 🔹 **Create a Virtual Environment**

#### **MacOS/Linux**
```bash
python3 -m venv venv
```

#### **Windows**
```bash
python -m venv venv
```

---

### 🔹 **Activate Virtual Environment**

#### **MacOS/Linux**
```bash
source venv/bin/activate
```

#### **Windows**
```bash
venv\Scripts\activate
```

---

### 🔹 **Install Dependencies**
```bash
pip install -r requirements.txt
```

---

### 🔹 **For NixOS (No venv required)**
```nix
nix develop
```

---

## 🚀 Running the Application

### 🔹 **For Development**
```bash
uvicorn app:app --reload
```

### 🔹 **For Production (4 Workers)**
```bash
gunicorn -k uvicorn.workers.UvicornWorker -w 4 -b 0.0.0.0:8080 app.main:app
```

---

Let me know if you need additional improvements like **Docker setup, environment variables, or logging**! 🚀✨

