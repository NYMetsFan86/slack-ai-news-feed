# 🎙️ Adding Custom Podcasts Guide

This guide explains how to add new podcasts to the AI News Summarizer, including Spotify-exclusive shows.

## 📡 Finding Podcast RSS Feeds

### Method 1: Direct RSS (Easiest)

Many podcasts provide RSS feeds directly:

1. **Check the podcast website** - Look for RSS icon or "Subscribe" links
2. **Search online** - Google "[podcast name] RSS feed"
3. **Common podcast platforms with RSS**:
   - Apple Podcasts - All shows have RSS
   - Google Podcasts - Most have public RSS
   - Podcast hosting platforms (Transistor, Buzzsprout, etc.)

### Method 2: Extract from Platform URLs

Use these tools to extract RSS from platform URLs:

#### For Spotify Podcasts

1. **Get-RSS.com** (Recommended)
   - Visit: https://www.get-rss.com
   - Paste Spotify URL: `https://open.spotify.com/show/[SHOW_ID]`
   - Click "Extract RSS"
   - Copy the resulting RSS URL

2. **RSS Feed ASAP**
   - Visit: https://rssfeedasap.com/rss-feed-from-spotify
   - Enter Spotify podcast URL
   - Get extracted RSS feed

3. **EachPod RSS Finder**
   - Visit: https://eachpod.com/tools/podcast-rss-feed-finder/
   - Works with multiple platforms

#### For Apple Podcasts

- Right-click on podcast in Apple Podcasts
- Select "Copy Link"
- Use the ID from the URL with: `https://podcasts.apple.com/podcast/id[PODCAST_ID]/feed`

## 🔧 Adding to Configuration

### Step 1: Test the RSS Feed

Before adding, verify the feed works:

```bash
# Run the RSS feed tester
python tests/test_rss_feed.py
```

Or test manually:
```bash
curl -I "https://your-rss-feed-url.xml"
```

### Step 2: Add to Configuration

Edit `src/config.py`:

```python
PODCAST_FEEDS = [
    # ... existing feeds ...
    {
        "name": "Your Podcast Name",
        "url": "https://your-rss-feed-url.xml",
        "type": "podcast"
    }
]
```

### Step 3: Deploy Changes

```bash
# Rebuild and deploy
make build
make deploy
```

## 🎯 Real Example: Adding "AI News in 5 Minutes or Less"

We recently added this Spotify podcast to the configuration:

1. **Original Spotify URL**: 
   ```
   https://open.spotify.com/show/2Odqtd6gkFtUipUfb0jeOi
   ```

2. **Extracted RSS Feed**:
   ```
   https://feeds.transistor.fm/ai-news-in-5-minutes-or-less
   ```

3. **Added to config.py**:
   ```python
   {
       "name": "AI News in 5 Minutes or Less",
       "url": "https://feeds.transistor.fm/ai-news-in-5-minutes-or-less",
       "type": "podcast"
   }
   ```

## ⚠️ Troubleshooting

### Feed Not Working?

1. **Check if it's platform-exclusive**
   - Some Spotify Originals don't have RSS
   - Apple Podcasts+ exclusive content

2. **Verify the URL**
   - Open in browser - should show XML
   - Check for redirects

3. **Test with feedparser**:
   ```python
   import feedparser
   feed = feedparser.parse("YOUR_RSS_URL")
   print(f"Valid: {not feed.bozo}")
   print(f"Entries: {len(feed.entries)}")
   ```

### Common Issues

| Issue | Solution |
|-------|----------|
| 403 Forbidden | Add User-Agent header in `rss_parser.py` |
| No episodes found | Check if feed uses different date fields |
| Encoding errors | Ensure feed returns valid UTF-8 |
| Timeout | Increase `REQUEST_TIMEOUT` in config |

## 🚀 Advanced: Custom Feed Processing

For podcasts with unique formats, create a custom parser:

```python
# In src/rss_parser.py
def extract_feed_items(self, feed, feed_config, hours_back=24):
    # Add special handling
    if feed_config['name'] == "Special Podcast":
        # Custom extraction logic
        return self._extract_special_podcast(feed)
    
    # Default processing
    return super().extract_feed_items(feed, feed_config, hours_back)
```

## 📋 Podcast Feed Quality Checklist

Before adding a podcast, ensure:

- [ ] RSS feed is publicly accessible
- [ ] Feed updates when new episodes release
- [ ] Episode descriptions contain useful content
- [ ] Feed includes publication dates
- [ ] No authentication required
- [ ] Reasonable update frequency (daily/weekly)

## 🎙️ Recommended AI Podcasts

Here are some AI-focused podcasts with reliable RSS feeds:

1. **The AI Podcast** (NVIDIA)
   - RSS: `https://feeds.buzzsprout.com/1770932.rss`
   
2. **Practical AI**
   - RSS: `https://feeds.megaphone.fm/STP1067272780`

3. **AI News in 5 Minutes or Less**
   - RSS: `https://feeds.transistor.fm/ai-news-in-5-minutes-or-less`

4. **Eye on AI**
   - RSS: `https://feeds.transistor.fm/eye-on-ai`

5. **The Gradient Podcast**
   - RSS: `https://feeds.transistor.fm/the-gradient-podcast`

## 📝 Contributing New Feeds

If you find a great AI podcast:

1. Test the RSS feed thoroughly
2. Add to your local config
3. Run for a few days to verify
4. Submit a pull request with:
   - Feed configuration
   - Test results
   - Why it's valuable for AI news