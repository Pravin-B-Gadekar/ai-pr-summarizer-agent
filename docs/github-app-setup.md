# GitHub App Setup Guide

Follow these steps to create and configure your GitHub App:

## 1. Create a New GitHub App

1. Go to your GitHub account settings
2. Navigate to "Developer settings" > "GitHub Apps" 
3. Click "New GitHub App"
4. Fill in the following details:
   - **GitHub App name**: PR Review Bot (or any name you prefer)
   - **Homepage URL**: Can be your GitHub profile or the URL to your bot once deployed
   - **Webhook URL**: Leave blank for now (you'll update this after deployment)
   - **Webhook secret**: Optional but recommended for security
   - **Repository permissions**:
     - **Pull requests**: Read & Write
     - **Contents**: Read-only
     - **Metadata**: Read-only
   - **Subscribe to events**:
     - **Pull request**
5. Create the app

## 2. Generate a Private Key

1. After creating the app, scroll down to the "Private keys" section
2. Click "Generate a private key"
3. Save the downloaded .pem file securely

## 3. Install the App

1. In your GitHub App page, click "Install App"
2. Choose the repositories where you want to use the PR Review Bot
3. Complete the installation

## 4. Get Required Information

You'll need the following information for your environment variables:

1. **App ID**: Found on your GitHub App's page
2. **Installation ID**: 
   - Go to `https://api.github.com/users/YOUR_USERNAME/installation`
   - Look for the `id` field in the response
3. **Private Key**: The contents of the .pem file you downloaded
   - For Render deployment, you'll need to format this properly (see deployment guide)

## 5. Update Webhook URL (After Deployment)

1. Once your bot is deployed on Render, get your application URL
2. Go back to your GitHub App settings
3. Update the Webhook URL with your Render URL + "/webhook" (e.g., https://your-app.onrender.com/webhook)
4. Save changes
