# Instructions for Claude Code (IDE Terminal Prompts - Google Cloud Edition)

This file contains the sequence of prompts you should send to "Claude Code" in your Cursor IDE terminal to generate the `main.py` script for the AI News & Podcast Summarizer. This version is tailored for Google Cloud Platform services (Cloud Functions, Cloud Firestore, Cloud Scheduler/PubSub). Follow these prompts in the exact order specified.

---

### Prompt 1: Generate .env file content

Please generate the full content for a .env file. Include placeholders for OPENROUTER_API_KEY and a SLACK_WEBHOOK_URL. Also, add a comment explaining that I need to fill in these values. Make sure the HTTP-Referer is set to a generic placeholder like my-company-ai-app as required by OpenRouter. Additionally, include a placeholder for GOOGLE_CLOUD_PROJECT for the GCP project ID.


### Prompt 2: Generate initial main.py with basic setup and imports

Now, generate a Python script named main.py. Include all necessary imports for os, requests, BeautifulSoup, OpenAI, dotenv, and google.cloud.firestore. Add load_dotenv() conditional to if name == "main": for local testing. Add a function get_openrouter_client() that initializes and returns an openai.OpenAI client configured for OpenRouter, loading the API key from the environment and setting the HTTP-Referer header. Also, add a function get_firestore_client() that initializes and returns a Google Cloud Firestore client.


### Prompt 3: Add functions for tracking processed items in Firestore

Add two functions to main.py: is_item_processed(item_url, firestore_client, collection_name='processed_items') and mark_item_processed(item_url, firestore_client, collection_name='processed_items'). is_item_processed should query the specified Firestore collection to check if a document with the given item_url (as its ID or a field) exists. mark_item_processed should add a new document to the collection with the item_url and a processed_at timestamp. Include robust error handling for Firestore operations.


### Prompt 4: Add a function to scrape an article from a URL

Add a function fetch_article_content(url) to main.py. This function should use requests to get the webpage content and BeautifulSoup to parse the HTML. It should aim to extract the main readable text content (e.g., from <p> tags, or a common article div) and return it as a string, truncating it to 8000 characters to fit LLM context windows. Include robust error handling for network requests or parsing issues, returning None on failure.


### Prompt 5: Add a function to summarize content using a free OpenRouter LLM

Add a function summarize_content(text, client, model_name) to main.py. This function should take the text, the OpenRouter client, and the model name, then use client.chat.completions.create to generate a 3-5 point bulleted summary. Include a system message instructing the model to be concise and highlight key information. Add robust error handling, returning a default message if summarization fails. Include a comment reminding me to choose a currently free model from OpenRouter for model_name when I implement this.


### Prompt 6: Add a function to generate an AI Tip of the Day

Add a new function generate_ai_tip(client, model_name) to main.py. This function should use the OpenRouter client and a free model to generate a concise, engaging 'AI Tip of the Day' (e.g., a practical usage tip, a concept explanation, or a best practice for prompt engineering). The output should be a short paragraph or a couple of bullet points. Include robust error handling.


### Prompt 7: Add a function to post messages to Slack

Add a function post_to_slack(title, content, url, webhook_url) to main.py. This function should take a title, the main content (summary or tip), an optional URL, and the Slack webhook URL. It should format the message using Slack's Block Kit (specifically section and context blocks) for clear presentation. Include robust error handling for the HTTP POST request.


### Prompt 8: Complete the main.py script with the main execution logic

Complete the main.py script. Create a main_function(event, context) function (for Google Cloud Functions compatibility with Pub/Sub trigger) that orchestrates the workflow. Inside it:

Initialize the OpenRouter client and Google Cloud Firestore client.

Call generate_ai_tip and post_to_slack for the AI Tip of the Day.

Define a list of example news RSS feed URLs and podcast RSS feed URLs (where we will summarize the description, not audio).

Loop through each RSS feed entry:
a. Check if the item is already processed using is_item_processed.
b. For news, call fetch_article_content and then summarize_content.
c. For podcasts, extract the summary or description from the RSS entry and then call summarize_content.
d. Post the summarized content to Slack using post_to_slack.
e. Mark the item as processed using mark_item_processed.

Include comprehensive logging (print statements are fine for now, will transition to logging in production) and error handling for the entire flow. Structure it to handle both news and podcast feeds within the same execution.


### Prompt 9: Generate a requirements.txt file for deployment

Generate the complete content for a requirements.txt file based on the libraries used in this project: openai, python-dotenv, requests, beautifulsoup4, and google-cloud-firestore.


### Prompt 10: Provide a brief, step-by-step guide on how to deploy and test the script

Give me a simple, one-paragraph explanation of how to prepare your code for Google Cloud Functions deployment (packaging dependencies) and how to configure a basic scheduled trigger (Cloud Scheduler via Pub/Sub). Also, explain how to test it by checking your Slack channel and Cloud Firestore database.