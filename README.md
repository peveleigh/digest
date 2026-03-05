# Digest

A Python-based news scraper and summarizer that fetches articles from RSS feeds, stores them in a database, and sends summarized digests via Gotify.

## Features

- **Scrape**: Fetches news articles from sources defined in `feeds.json`.
- **Summarize**: Generates AI-powered summaries of recent articles using OpenAI.
- **Notify**: Sends summaries to a Gotify server.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure environment variables in a `.env` file:
   ```env
   DATABASE_URL=your_postgres_url
   API_KEY=your_openrouter_api_key
   MODEL=your_llm_model_of_choice
   USER_AGENT=your_user_agent
   GOTIFY_URL=your_gotify_url
   GOTIFY_TOKEN=your_gotify_token
   ```

3. Create a `feeds.json` file containing the RSS feeds you want to scrape:
   ```json
   [
     {
       "url": "https://example.com/rss-world-news",
       "category": "world"
     },
     {
       "url": "https://example.com/rss-business-news",
       "category": "business"
     },
   ]
   ```

4. Initialize the database:
   ```bash
   python -m digest.init_db
   ```

## Usage

Run the application using the following commands:

### Scrape News
```bash
python -m digest scrape
```

### Generate and Send Summaries
```bash
python -m digest summarize
```
