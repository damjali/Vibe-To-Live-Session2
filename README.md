# ☁️ GDGoC UM Cloud Workshop: *Vibe To Live* 🦖🏎️

Welcome to the **GDGoC UM Cloud Workshop**!
In this session, you will learn how to deploy a **real-time multiplayer game** using **Serverless Architecture with Google Cloud Run**.

By the end of this guide, your game will be **live on the internet** and playable with your friends 🎮

---

## 🚀 Section 1: Run the Game Locally (Single Player)

First, let's run the game on your own computer to see how it works locally.

### 1. Create and Activate a Virtual Environment

Navigate to the `backend` folder and set up a Python virtual environment:

**Windows:**
```powershell
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

**macOS / Linux:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Start the Backend Server

Once dependencies are installed, start the FastAPI server:

```bash
uvicorn main:app --reload
```

### 3. Open in Browser

Go to the following URL in your web browser:
👉 `http://localhost:8000/`

✅ At this point, your game is running locally!
❌ But… you're playing alone 😢

---

## 🌐 Section 2: Deploy Online (Multiplayer with Cloud Run)

Now let's make your game **public and multiplayer** so others can join!

### Step 1: Claim GCP Credits and Enable Services

1. Claim your free $5 GCP credit (if applicable).
2. Open the **Google Cloud Console**.
3. Go to the **Billing** section and open **Linked Accounts**.
4. Set the billing account for your current project to the **Google Cloud Platform Trial Billing Account**.

Open **Google Cloud Shell** from the console, and enable the required services:

```bash
gcloud services enable compute.googleapis.com run.googleapis.com cloudbuild.googleapis.com
```

### Step 2: Clone the Project in Cloud Shell

In your Cloud Shell, run the following commands to get the project files:

```bash
git clone https://github.com/damjali/Vibe-To-Live-Session2.git
cd Vibe-To-Live-Session2
```

### ⚠️ Step 3: Set Project Info & Permissions (IMPORTANT)

Before building, you must configure your **Project ID, Project Number, and permissions**.

#### 1. Get Project ID & Number

```bash
export PROJECT_ID=$(gcloud config get-value project)
export PROJECT_NUM=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
```

#### 2. Grant Required Permissions

Grant the default compute service account the necessary permissions to build and deploy to Cloud Run:

```bash
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${PROJECT_NUM}-compute@developer.gserviceaccount.com" \
  --role="roles/run.builder"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${PROJECT_NUM}-compute@developer.gserviceaccount.com" \
  --role="roles/editor"
```

✅ This allows Cloud Run to:
* Build your container
* Deploy and manage services

### Step 4: Create Artifact Registry & Build Docker Image

First, create a repository inside Artifact Registry for the project:

```bash
gcloud artifacts repositories create vibe-to-live \
    --repository-format=docker \
    --location=asia-southeast1 \
    --description="Docker repository for Vibe-To-Live project"
```

Then, submit the build using Google Cloud Build:

```bash
gcloud builds submit \
    --tag asia-southeast1-docker.pkg.dev/$PROJECT_ID/vibe-to-live/sumo-wars:latest .
```

### Step 5: Deploy to Cloud Run

Once the image is built, deploy it via the Google Cloud Console:

1. Go to **Cloud Run** in the Google Cloud Console.
2. Click on **Services** and then **Deploy Container**.
3. Under **Container Image URL**, select the `sumo-wars` image you just built.
4. Configure the following settings:
   - **Container Port:** `8000`
   - **Region:** `asia-southeast1 (Singapore)`
   - **Minimum Instances:** `0`
   - **Maximum Instances:** `1` *(Optional: Keeps everyone in the same server instance)*
   - **Authentication:** ✅ Allow **unauthenticated invocations** (Public access)
5. Click **Create**.

### Step 6: Play Multiplayer 🎮

After deployment is complete:

* You’ll get a **public URL** for your Cloud Run service.
* Open it in your browser.
* Share the link with your friends!

🔥 Now multiple players can join your game at the same time!

---

## 🎉 Congratulations!

You’ve successfully:
✔️ Run a backend server locally.
✔️ Set up Google Cloud Platform with necessary permissions.
✔️ Built a Docker image and stored it in Artifact Registry.
✔️ Deployed a serverless multiplayer game using Cloud Run.

Now go share your game and play together! 🚀
