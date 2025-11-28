📌 Overview

This Power BI dashboard visualizes 12 months of YouTube data from 10 major Indian tech channels.
It converts raw API data into interactive, insight-driven visuals to understand:

Upload patterns

Long-form vs short-form performance

Engagement behavior

Monthly view cycles

Creator strategy archetypes

High-performing video traits

This is the BI layer of the project — designed to communicate insights at a glance, with drilldowns for deeper investigation.

🛠️ Power BI Workflow
1️⃣ Data Loading

Imported pre-cleaned CSVs generated from Python:

channels.csv

videos.csv

monthly_stats.csv

video_details.csv

Each file was connected through relationships based on:

channelId

videoId

publishedAt (for time-series)

2️⃣ Data Modeling

Inside Power BI, I:

✔ Built relationships (Star Schema)

Channels (Dimension)

Videos (Fact)

MonthlyStats (Fact)

VideoDetails (Fact)

✔ Created custom DAX measures such as:

Engagement Ratio

Views-to-ContentType

Upload Frequency

Shorts-to-Videos Ratio

Views per Minute

Top Content by Month

Duration Buckets (0–30s, 30–60s, 1–3min, 3–10min, 10+ min)

✔ Built calculated tables

For duration grouping and monthly summaries.

The model was optimized to ensure snappy slicers, quick filter changes, and smooth cross-interaction.

🖥️ Dashboard Pages Breakdown
🔴 Page 1 — Creator Landscape Overview

A top-level summary of the entire dataset including:

Total videos (28K)

Total shorts (3.11K)

Total duration (2M minutes)

Average subscribers (7.9M)

Channel-level rankings:

Subscribers

Views

Total videos

Visuals used:

Bar charts

Donut charts

KPI cards

Comparative bars for long vs short form

This page gives an instant market-level snapshot.

🔵 Page 2 — Quantity vs Quality Analysis

Focus: Does uploading more make a creator grow faster?

Visuals:

Subscribers vs Total Videos (scatter)

Subscribers vs Total Views (scatter)

A narrative textbox

Correlation understanding

This is where the insight “Quality beats quantity” becomes visually obvious.

🔴 Page 3 — Creator Deep Dive (Technical Guruji Example)

This is the most advanced page in the report.

Features:

Channel selector (slicer)

Content-type bar (videos vs shorts)

Monthly view trends

Engagement ratio by month

Upload frequency per month

Duration vs engagement visualization

Top 10+ performing videos table with:

Views

Likes

Comments

Month

Content type

This page is designed like a creator analytics console.

🟢 Page 4 — Engagement Contribution + Long vs Short Form

Purpose: Understand how different content types contribute to total engagement.

Highlights:

Shorts vs Video contributions

Top channels by views

Upload type selection

KPI cards for:

Total long videos

Total shorts

Total views from each

This page makes it clear that long videos carry long-term view volume, while shorts spike discoverability.

🔵 Page 5 — Strategic Insights

A clean, executive-level summary page that outlines:

✔ Creator Strategy Archetypes

Long-Form Titans

Hybrid Strategists

Shorts-Heavy Experimenters

✔ What Works (Data-backed)

Deep long-form videos

Launch-cycle alignment

Strategic shorts

Consistent upload cadence

✔ What Doesn’t

Shorts spam

Weak-topic long videos

Skipping peak months

This is built for hiring managers, marketers, and stakeholders to quickly understand the story.

📈 Key BI Skills Demonstrated

This Power BI component showcases:

Data modeling (star schema)

DAX calculations

Time-intelligence functions

Measure optimization

Cross-page filtering

UX-friendly design

Color-coded storytelling

Drill-down insights

KPI-driven BI reporting

This is beyond “just charts” — it’s a full BI solution.
