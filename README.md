# AI News & Podcast Summarizer for Company Awareness (Google Cloud Edition)

## Overview

This project implements a lightweight, serverless application designed to boost AI awareness and knowledge within your company. It automatically fetches and summarizes relevant news articles and podcast descriptions using a Large Language Model (LLM), and generates a daily "AI Tip of the Day," then posts all this curated content directly to a Slack channel.

The core philosophy is "low drag" – meaning minimal operational overhead, low maintenance, and cost-effective execution, primarily utilizing free LLM models via OpenRouter and Google Cloud Platform's generous free-tier services. All infrastructure components are centralized within a single Google Cloud Project.

## Features

* **Automated News & Podcast Summaries:** Fetches content from configured RSS feeds and summarizes it into concise, bulleted points.
    * *News Articles:* Scrapes full article content and summarizes.
    * *Podcasts:* Summarizes episode descriptions/show notes (does NOT process audio).
* **Daily AI Tip:** Generates an engaging and educational "AI Tip of the Day" on topics like practical AI usage, core concepts, or prompt engineering.
* **Duplicate Prevention:** Ensures that articles/episodes are summarized and posted only once using Google Cloud Firestore.
* **Slack Integration:** Delivers all content in a clear, formatted manner to a specified Slack channel.
* **Serverless & Cost-Effective:** Runs on Google Cloud Functions, uses Cloud Firestore for state management, and leverages free LLM models from OpenRouter to keep costs minimal, well within free tier limits for typical usage.

## Architecture

The application is built with a serverless architecture on Google Cloud Platform:

* **Google Cloud Functions:** The core compute service, executing the Python script.
* **Google Cloud Firestore:** A NoSQL database used to store URLs of already processed items, preventing duplicate Slack posts.
* **Google Cloud Scheduler:** Triggers the Cloud Function on a defined schedule (e.g., daily at 7 AM MST on weekdays).
* **Google Cloud Pub/Sub:** Acts as the messaging layer between Cloud Scheduler and Cloud Functions.
* **OpenRouter:** Serves as the API endpoint for various LLMs, allowing flexible selection of free models for summarization and tip generation.
* **Slack Incoming Webhooks:** Used for posting messages to your designated Slack channel.

```mermaid
graph TD
    A[Google Cloud Scheduler] -- Publishes Message --> B(Google Cloud Pub/Sub Topic);
    B -- Triggers --> C(Google Cloud Function);
    C --> D{RSS Feeds / Web Pages};
    D --> E[Requests & BeautifulSoup];
    E --> F[LLM via OpenRouter];
    F --> G[Slack Webhook];
    C --> H(Google Cloud Firestore);
    H -- Read/Write --> C;
    F -- AI Tip of Day --> G;