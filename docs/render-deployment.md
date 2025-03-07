# Render Deployment Guide

Follow these steps to deploy your PR Review Bot on Render:

## 1. Prepare Your Repository

1. Create a new repository on GitHub
2. Add the following files to your repository:
   - `app.py` (the main Python file)
   - `requirements.txt`
   - `render.yaml` (optional, for Blueprint deployments)
   - `.env.template` (as a reference, don't include actual secrets)

## 2. Sign Up for Render

1. Go to [render.com](https://render.com/)
2. Sign up for a free account (you can sign up with your GitHub account)

## 3. Create a New Web Service

1. From the Render dashboard, click "New" and select "Web Service"
2. Connect your GitHub repository
3. Configure the service:
   - **Name**: pr-review-bot (or any name you prefer)
   - **Environment**: Python
   - **Region**: Choose the one closest to you
   - **Branch**: main (or your preferred branch)
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --worker-class=gthread --workers=1 --threads=8 --timeout=0 'app:app'`

## 4. Configure Environment Variables

Add the following environment variables in the Render dashboard:

1. **GITHUB_APP_ID**: Your GitHub App ID
2. **GITHUB_PRIVATE_KEY**: Your GitHub App private key
   - Note: For multiline private keys, replace newlines with `\n` characters
   - Example: `-----BEGIN RSA PRIVATE KEY-----\nMIIEpAIBAAKCAQEA...\n-----END RSA PRIVATE KEY-----`
3. **GITHUB_INSTALLATION_ID**: Your GitHub App installation ID
4. **GEMINI_API_KEY**: Your Google Gemini API key

## 5. Deploy the Service

1. Click "Create Web Service"
2. Wait for the deployment to complete (this may take a few minutes)
3. Once deployed, you'll get a URL for your service (e.g., `https://pr-review-bot.onrender.com`)

## 6. Update GitHub App Webhook

1. Go to your GitHub App settings
2. Update the Webhook URL to your Render app URL + "/webhook"
   - Example: `https://pr-review-bot.onrender.com/webhook`
3. Save changes

## 7. Testing Your Deployment

1. Create a new pull request in a repository where your GitHub App is installed
2. Verify that the bot posts a comment on the PR
3. Check the logs in the Render dashboard for any errors

## 8. Troubleshooting

If your bot isn't working properly:

1. Check the logs in the Render dashboard
2. Verify that all environment variables are set correctly
3. Ensure your GitHub App has the necessary permissions
4. Check that the webhook URL is correctly configured
5. Confirm that your GitHub App is installed on the repository where you're creating PRs

## 9. Free Tier Limitations

Remember that Render's free tier has some limitations:

- Services sleep after 15 minutes of inactivity
- Limited build minutes per month
- Limited bandwidth

For a production environment, you might want to consider upgrading to a paid plan.
