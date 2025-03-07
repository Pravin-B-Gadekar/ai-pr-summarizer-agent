# Google Gemini API Setup Guide

Follow these steps to get set up with the Google Gemini API:

## 1. Create a Google AI Studio Account

1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Sign in with your Google account
3. Accept the terms of service

## 2. Get an API Key

1. From the AI Studio dashboard, click on "Get API key" in the top-right corner
2. If you don't already have an API key, you'll be prompted to create one
3. Click "Create API key"
4. Give your API key a name (e.g., "PR Review Bot")
5. Copy the API key string and store it securely
   - **Important**: The API key will only be shown once

## 3. Understand Pricing and Limits

As of March 2025, Google offers:

1. **Free Tier**:
   - Limited number of requests per minute
   - Limited total tokens per month
   - Access to Gemini 1.5 Pro and other models

2. **Paid Tier**:
   - Higher rate limits
   - Pay-as-you-go pricing based on input and output tokens

Check the [Gemini API pricing page](https://ai.google.dev/pricing) for the most current information.

## 4. Test Your API Key

Before integrating with your PR Review Bot, you can test your API key:

```python
import google.generativeai as genai

# Configure the API
genai.configure(api_key="YOUR_API_KEY")

# Test with a simple prompt
model = genai.GenerativeModel('gemini-1.5-pro')
response = model.generate_content("Hello, how are you?")
print(response.text)
```

## 5. Add Your API Key to Environment Variables

1. In your local development environment:
   - Add `GEMINI_API_KEY=your_api_key` to your `.env` file

2. For Render deployment:
   - Add the `GEMINI_API_KEY` environment variable in the Render dashboard
   - Keep it as a secret environment variable

## 6. Troubleshooting

If you encounter issues with the API:

1. **Rate Limiting**: If you see errors related to rate limits, you may need to implement retry logic or upgrade to a paid tier
2. **Content Filtering**: Gemini has built-in safety filters that may block certain prompts
3. **Token Limits**: Check that your prompts aren't exceeding the maximum token limit
