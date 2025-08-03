# AI News & Podcast Summarizer for Company Awareness (Google Cloud Edition)

## 1. Introduction

This document outlines the specifications for a serverless application designed to enhance AI awareness and knowledge within the company. The application will leverage Large Language Models (LLMs) to summarize relevant news articles and podcast descriptions, and to generate a daily "AI Tip of the Day," delivering all content to a designated Slack channel. The primary goal is to provide concise, valuable AI-related information with minimal operational overhead and cost, specifically leveraging Google Cloud Platform (GCP) services.

## 2. Goals & Objectives

* **Increase AI Awareness:** Regularly disseminate AI-related news and concepts to all employees via a familiar communication channel (Slack).
* **Enhance AI Knowledge:** Provide digestible summaries of complex topics and actionable "AI Tips of the Day" to foster continuous learning.
* **Low Operational Drag:** Implement a serverless architecture on GCP to minimize infrastructure management, maintenance, and ongoing costs.
* **Cost-Effectiveness:** Utilize GCP's free-tier services (Cloud Functions, Cloud Firestore, Cloud Scheduler) and free LLM models (via OpenRouter) to keep expenses at a minimum for daily scheduled runs.
* **Timely Information:** Deliver daily updates to keep the company informed on the latest in AI.
* **Centralized Management:** Consolidate all infrastructure components within a single Google Cloud Project for ease of management and reduced platform sprawl.

## 3. Core Features

* **News Article Summarization:**
    * Fetches content from predefined RSS news feeds.
    * Extracts main article text from URLs.
    * Summarizes extracted text into 3-5 bullet points using an LLM.
    * Posts summary, original title, and URL to Slack.
* **Podcast Description Summarization:**
    * Fetches content from predefined podcast RSS feeds.
    * Extracts episode descriptions/show notes from the RSS feed (does NOT transcribe audio).
    * Summarizes descriptions into 3-5 bullet points using an LLM.
    * Posts summary, episode title, and URL to Slack.
* **AI Tip of the Day Generation:**
    * Generates a concise, engaging, and educational "AI Tip of the Day" using an LLM.
    * Tips can cover practical usage, foundational concepts, ethical considerations, or prompt engineering basics.
    * Posts the AI Tip to Slack.
* **Duplicate Prevention:**
    * Utilizes a persistent storage (Google Cloud Firestore) to track previously processed URLs, preventing redundant posts.
* **Slack Integration:**
    * All summarized content and AI tips are formatted for clear readability in Slack using Block Kit elements.
* **Serverless Execution:**
    * Designed to run as a Google Cloud Function, triggered by a schedule (7 AM MST on weekdays via Cloud Scheduler).

## 4. Technical Architecture (Google Cloud Focus)

* **Cloud Provider:** Google Cloud Platform (GCP)
* **Compute:** Google Cloud Functions
    * Python 3.x runtime.
    * Triggered by Google Cloud Scheduler (via Pub/Sub topic).
    * Environment variables for API keys and Slack webhook URL.
    * Packaged with necessary Python dependencies.
* **Database:** Google Cloud Firestore (Native Mode)
    * A single collection (e.g., `processed_items`) to store processed item URLs and timestamps.
    * Document ID will be the URL (or a hashed version), with a `processed_at` field.
    * Used to prevent reprocessing and duplicate Slack posts.
* **Scheduler:** Google Cloud Scheduler
    * Configured with a cron expression (e.g., `0 14 * * 1-5` for 7 AM MST Mon-Fri, accounting for UTC conversion).
    * Publishes a message to a Google Cloud Pub/Sub topic.
* **Messaging (for Scheduler Trigger):** Google Cloud Pub/Sub
    * A lightweight messaging service. Cloud Scheduler publishes to a topic, and the Cloud Function subscribes to it.
* **Storage (for Function Deployment):** Google Cloud Storage
    * Used implicitly by Cloud Functions to store your deployed code package.
* **LLM Provider:** OpenRouter
    * Acts as a unified API for various LLMs.
    * Selected for its support of multiple free-tier LLM models.
* **Content Fetching:**
    * `requests` library for HTTP requests (RSS feeds, article content).
    * `BeautifulSoup` for parsing HTML to extract main article text.
* **Communication:** Slack Incoming Webhook.
* **Libraries:** `openai` (for OpenRouter API), `python-dotenv`, `requests`, `beautifulsoup4`, `google-cloud-firestore`, `google-cloud-pubsub`.