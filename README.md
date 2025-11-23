📌 YouTube Channel Video Extractor — Streamlit Dashboard

A clean, modern Streamlit dashboard that extracts complete YouTube video data from any channel (or multiple channels) using the YouTube Data API v3.

Supports months-based filtering, batch extraction, auto-short detection, and CSV export — no terminal required.

🚀 Features
🎛️ Streamlit UI

Extract data for one channel

Extract data from multiple channels (batch mode)

Input months to look back

Paste or upload channel ID lists

Download final CSV

Live logs + progress bar

📊 Extracted Fields
Field	Description
channelID	The channel ID
channelName	Channel name
videoID	Unique video identifier
videoTitle	Title of the video
duration	Duration in seconds
isShort	TRUE if video < 60 sec
views	View count
likes	Likes
comments	Comment count
tags	Pipe-separated tags
thumbnail	High-res thumbnail URL
publishedDate	Publish timestamp
description	Full video description
⚡ Reliable API Usage

Retry logic (3 attempts)

Timeout handling

Graceful error messages
