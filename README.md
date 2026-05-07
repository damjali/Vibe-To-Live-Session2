# ☁️ GDGoC UM Cloud Workshop: *Vibe To Live* 🦖🏎️

Welcome to the **GDGoC UM Cloud Workshop**!  
In this session, you will learn how to deploy a **real-time multiplayer game** using **Serverless Architecture with Google Cloud Run**.

By the end of this guide, your game will be **live on the internet** and playable with your friends 🎮

---

# 📋 Prerequisites

Before starting the workshop, make sure you have the following installed on your laptop:

## ✅ Required Software

---

## 1. Install Python

Download and install Python (version 3.10 or newer recommended):

- Windows/macOS/Linux:
  - https://www.python.org/downloads/

⚠️ During installation on Windows, make sure to check:

- ✅ “Add Python to PATH”

---

## 2. Check if Python is Added to PATH

After installation, open:

- Windows → Command Prompt / PowerShell
- macOS/Linux → Terminal

Run:

```bash
python --version
```

Expected output example:

```bash
Python 3.11.0
```

If you see:

```bash
python is not recognized
```

then Python is not added to PATH correctly.

---

### Windows Fix (If Python Not Found)

Reinstall Python and ensure this is checked during installation:

✅ `Add Python to PATH`

OR manually add Python to PATH through:

- System Environment Variables
- Edit PATH
- Add your Python installation folder

---

## 3. Install Node.js & npm

Download Node.js (LTS version recommended):

- https://nodejs.org/

Installing Node.js will also install `npm`.

---

## 4. Verify npm Installation

Run:

```bash
npm --version
```

Expected output example:

```bash
10.5.0
```

---

## 5. Install Git

Download Git:

- https://git-scm.com/downloads

After installing Git, configure your Git identity:

```bash
git config --global user.name "Your Name"
git config --global user.email "your-email@example.com"
```

---

# 🚀 Section 1: Run the Game Locally (Single Player)

First, let's run the game on your own computer to see how it works locally.

---

## 1. Clone the Repository

```bash
git clone https://github.com/damjali/Vibe-To-Live-Session2.git
cd Vibe-To-Live-Session2
```

---

## 2. Create and Activate a Virtual Environment

Navigate to the `backend` folder and set up a Python virtual environment:

### Windows

```powershell
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

### macOS / Linux

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## 3. Start the Backend Server

Once dependencies are installed, start the FastAPI server:

```bash
uvicorn main:app --reload
```

---

## 4. Open in Browser

Go to the following URL in your web browser:

👉 `http://localhost:8000/`

✅ At this point, your game is running locally!  
❌ But… you're playing alone 😢

---

# 🌐 Section 2: Deploy Online (Multiplayer with Cloud Run)

Now let's make your game **public and multiplayer** so others can join!

---

# ☁️ Step 1: Open Google Cloud Shell Properly

1. Open the **Google Cloud Console**
2. Make sure you are currently inside the correct project
3. Ensure this project has the **billing account linked**
4. Click the **Terminal / Cloud Shell icon** on the top-right corner of the console

⚠️ IMPORTANT:  
Before continuing, double check that your Cloud Shell terminal is using the project with billing enabled.

You can verify using:

```bash
gcloud config get-value project
```

---

# 💳 Step 2: Claim GCP Credits and Enable Services

1. Claim your free $5 GCP credit (if applicable)
2. Open the **Billing** section
3. Open **Linked Accounts**
4. Ensure your current project is linked to:
   - ✅ Google Cloud Platform Trial Billing Account

Enable the required services:

```bash
gcloud services enable \
    compute.googleapis.com \
    run.googleapis.com \
    cloudbuild.googleapis.com \
    artifactregistry.googleapis.com
```

---

# 📥 Step 3: Clone the Project in Cloud Shell

In your Cloud Shell terminal:

```bash
git clone https://github.com/damjali/Vibe-To-Live-Session2.git
cd Vibe-To-Live-Session2
```

---

# ⚠️ Step 4: Set Project Info & Permissions (IMPORTANT)

Before building, configure your Project ID, Project Number, and permissions.

---

## 1. Get Project ID & Number

```bash
export PROJECT_ID=$(gcloud config get-value project)
export PROJECT_NUM=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
```

---

## 2. Grant Required Permissions

Grant the default compute service account the necessary permissions:

```bash
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${PROJECT_NUM}-compute@developer.gserviceaccount.com" \
  --role="roles/run.builder"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${PROJECT_NUM}-compute@developer.gserviceaccount.com" \
  --role="roles/editor"
```

---

## 3. Grant Yourself Cloud Build Permissions

Replace `"your email"` with your Google Cloud account email:

```bash
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="user:your-email@gmail.com" \
    --role="roles/cloudbuild.builds.editor"
```

Example:

```bash
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="user:adam@gmail.com" \
    --role="roles/cloudbuild.builds.editor"
```

✅ This allows you to:
- Trigger Cloud Build jobs
- Build Docker containers
- Deploy services properly

---

# 📦 Step 5: Create Artifact Registry & Build Docker Image

First, create a repository inside Artifact Registry:

```bash
gcloud artifacts repositories create vibe-to-live \
    --repository-format=docker \
    --location=asia-southeast1 \
    --description="Docker repository for Vibe-To-Live project"
```

---

Then, submit the build using Google Cloud Build:

```bash
gcloud builds submit \
    --tag asia-southeast1-docker.pkg.dev/$PROJECT_ID/vibe-to-live/sumo-wars:latest .
```

---

### Step 6: Deploy to Cloud Run

Once the image is built, deploy it via the Google Cloud Console:

1. Go to **Cloud Run**
2. Click **Services** → **Deploy Container**
3. Under **Container Image URL**, select the `sumo-wars` image
4. Configure the following settings:

| Setting | Value |
|---|---|
| Container Port | `8000` |
| Region | `asia-southeast1 (Singapore)` |
| Minimum Instances | `0` |
| Maximum Instances | `1` *(Optional: Keeps everyone in the same server instance)* |
| Authentication | ✅ **Allow unauthenticated invocations (Public Access)** |

⚠️ IMPORTANT:  
Make sure you enable:

✅ **Allow unauthenticated invocations**  
✅ **Public Access**

Otherwise, other players will not be able to access your game URL.

5. Click **Create**

---

# 🎮 Step 7: Play Multiplayer

After deployment is complete:

- You’ll get a public URL for your Cloud Run service
- Open it in your browser
- Share the link with your friends

🔥 Now multiple players can join your game at the same time!

---

# 🎉 Congratulations!

You’ve successfully:

✔️ Installed Python, npm, and Git  
✔️ Verified Python PATH configuration  
✔️ Run a backend server locally  
✔️ Set up Google Cloud Platform with necessary permissions  
✔️ Built a Docker image and stored it in Artifact Registry  
✔️ Deployed a serverless multiplayer game using Cloud Run  

Now go share your game and play together! 🚀
