# ☁️ GDGoC UM Cloud Workshop: *Vibe To Live* 🦖🏎️

Welcome to the **GDGoC UM Cloud Workshop**!
In this session, you will learn how to deploy a **real-time multiplayer game** using **Serverless Architecture with Google Cloud Run**.

By the end of this guide, your game will be **live on the internet** and playable with your friends 🎮

---

# 🚀 Section 1: Run the Game Locally (Single Player)

First, we run the game on your own computer.

### 1. Activate Virtual Environment

Navigate to your project folder and activate the virtual environment:

```bash
cd backend\venv\Scripts
activate
```

Or from root:

```bash
.\backend\venv\Scripts\activate
```

---

### 2. Start the Backend Server

```bash
cd backend
uvicorn main:app --reload
```

---

### 3. Open in Browser

Go to:

```
http://localhost:8000/
```

✅ At this point, your game is running locally
❌ But… you're playing alone 😢

---

# 🌐 Section 2: Deploy Online (Multiplayer with Cloud Run)

Now we make your game **public and multiplayer**.

---
## Step 1: Open Google Cloud Shell

Go to **Google Cloud Console → Cloud Shell**

---

## Step 2: Clone the Project

```bash
git clone https://github.com/damjali/Vibe-To-Live-Session2.git
cd Vibe-To-Live-Session2
```

---

## Step 3: Build Docker Image

Run this command:

```bash
gcloud builds submit \
--tag asia-southeast1-docker.pkg.dev/YOUR_PROJECT_ID/vibe-to-live/sumo-wars:latest .
```

⚠️ Replace:

```
YOUR_PROJECT_ID
```

with your **own Google Cloud project ID**

---

## Step 4: Deploy to Cloud Run

1. Go to **Cloud Run**
2. Click **"Services"**
3. Click **"Deploy Container"**
4. Under **Container Image URL**, select the image you just built
5. Configure:

   * **Port:** `8000`
   * **Region:** `asia-southeast1 (Singapore)`
   * ✅ Allow **public access**
6. Click **Create**

---

## Step 5: Play Multiplayer 🎮

After deployment:

* You’ll get a **public URL**
* Open it in your browser
* Send it to your friends

🔥 Now multiple players can join your game at the same time!


# 🎉 Congrats!

You’ve successfully:

* Run a backend server locally
* Built a Docker image
* Deployed a serverless multiplayer game