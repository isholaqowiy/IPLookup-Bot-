# 🌍 IPLookup Bot

A lightweight, asynchronous Telegram Bot built with Python using `python-telegram-bot` and `aiohttp`. It pulls real-time diagnostic geolocations of public IP configurations dynamically.

## 🚀 Deployment Instructions for Render.com

### Step 1: Upload Project to GitHub
1. Create a clean workspace and move these files inside.
2. Initialize Git, stage your files, commit them, and push up to a private or public GitHub repository.

### Step 2: Establish a Background Worker on Render
1. Navigate to your **Render Dashboard**, click **New +**, and select **Background Worker**.
2. Connect your GitHub repository.

### Step 3: Deployment Configurations
Fill out the parameters on Render with the following criteria:
* **Runtime**: `Python`
* **Build Command**: 
  ```bash
  pip install -r requirements.txt

