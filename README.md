# PR Review Bot

A GitHub PR review bot that automatically analyzes pull requests using Google's Gemini AI and provides detailed code reviews.

## Features

- Watches for new pull requests in configured repositories
- Analyzes code changes with Google Gemini AI
- Posts detailed reviews as comments on pull requests
- Provides file-by-file analysis and overall suggestions

## Setup

1. Create a GitHub App (see [GitHub App Setup](docs/github-setup.md))
2. Get a Google Gemini API key (see [Gemini API Setup](docs/gemini-setup.md))
3. Deploy the bot on Render (see [Deployment Guide](docs/deployment.md))

## Local Development

1. Clone this repository
2. Create a `.env` file based on `.env.template`
3. Install dependencies: `pip install -r requirements.txt`
4. Run the server: `python app.py`
5. (Optional) Use a service like [smee.io](https://smee.io) to forward GitHub webhooks to your local server

## Configuration

Configure the bot behavior through environment variables:

- `GITHUB_APP_ID`: Your GitHub App ID
- `GITHUB_PRIVATE_KEY`: Your GitHub App private key
- `GITHUB_INSTALLATION_ID`: Your GitHub App installation ID
- `GEMINI_API_KEY`: Your Google Gemini API key
- `PORT`: The port to run the server on (default: 3000)

## How It Works

1. When a new PR is opened, GitHub sends a webhook event to the bot
2. The bot posts a placeholder comment on the PR
3. It retrieves the changed files and their contents
4. The bot sends the code changes to Google's Gemini AI for analysis
5. Gemini generates a structured review with suggestions
6. The bot updates the placeholder comment with the full review

## License

MIT
