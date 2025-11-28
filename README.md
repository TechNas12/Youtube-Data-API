# 📌 YouTube Channel Data Extractor — Streamlit Dashboard

A clean, modern **Streamlit dashboard** that extracts complete YouTube video data from any channel (or multiple channels) using the **YouTube Data API v3**.

Supports **months-based filtering**, **batch extraction**, **automatic Shorts detection**, and **CSV export** — all without using the terminal.

---

## 🚀 Features

### 🎛️ Streamlit UI
- Extract data for **one channel**
- Extract data from **multiple channels** (batch mode)
- Input **months to look back**
- Paste or upload **channel ID lists**
- Download final CSV
- Live logs + progress bar
- Error-resilient API calls

---

## 📊 Extracted Fields

| Field | Description |
|-------|-------------|
| `channelID` | The channel ID |
| `channelName` | Channel name |
| `videoID` | Unique video identifier |
| `videoTitle` | Title of the video |
| `duration` | Duration in seconds |
| `isShort` | TRUE if video < 60 sec |
| `views` | View count |
| `likes` | Likes |
| `comments` | Comment count |
| `tags` | Pipe-separated tags |
| `thumbnail` | High-res thumbnail URL |
| `publishedDate` | Publish timestamp |
| `description` | Full video description |

---

## ⚡ Reliable API Usage
- Built-in retry logic (3 attempts)
- Graceful fallback handling  
- Timeout protection  
- Clean JSON parsing  
- Centralized API utilities in `utils.py`

---

## 🗂️ Project Structure

```
youtube_extractor/
│── streamlit_app.py      # Streamlit dashboard UI
│── utils.py              # Helper functions (API calls, duration parsing)
│── main.py               # Optional CLI entry point
│── config.yaml           # Streamlit theme config
│── pyproject.toml        # uv/poetry setup
│── uv.lock               # Dependency lock
│── .python-version       # Python version pin
│── README.md             # This documentation
│── .gitignore            # Ignored files
│── .env                  # API keys (ignored)
└── __pycache__/          # Auto-generated cache
```

---

## 🔐 Environment Setup

Create a `.env` file inside the project:

```env
YT_DATA_API=YOUR_API_KEY_HERE
BASE=https://www.googleapis.com/youtube/v3
```

⚠️ **Do NOT commit your `.env` file.**  
Your `.gitignore` already ignores it.

Enable the YouTube Data API v3 here:  
👉 https://console.cloud.google.com/apis/credentials

---

## 🛠️ Installation

### 1️⃣ Clone the repository
```bash
git clone https://github.com/yourusername/youtube_extractor.git
cd youtube_extractor
```

### 2️⃣ Create and activate a virtual environment

**Using uv (recommended):**
```bash
uv venv
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows
```

**Using Python venv:**
```bash
python -m venv .venv
source .venv/bin/activate   # macOS/Linux
.venv\Scripts\activate      # Windows
```

### 3️⃣ Install dependencies

**If using uv:**
```bash
uv sync
```

**Or manually:**
```bash
pip install streamlit python-dotenv python-dateutil requests pandas isodate
```

---

## ▶️ Running the Streamlit App

```bash
streamlit run streamlit_app.py
```

Your app will open at:
```
http://localhost:8501
```

---

## 📥 Usage

### 🔹 Single Channel Mode
1. Enter the **YouTube Channel ID**
2. Select the **number of months** to look back
3. Click **Run extraction**
4. View or download the CSV

### 🔹 Batch Mode
1. Upload a `.txt` file containing channel IDs:
   ```
   UC123...
   UC456...
   UC789...
   ```
   Or paste IDs manually
2. Enter an **output label** for the CSV filename
3. Click **Run batch extraction**
4. Download the merged CSV: `yt_data_{label}.csv`

---

## 🧪 Example CSV Output

```csv
channelID,channelName,videoID,videoTitle,duration,isShort,views,likes,comments,tags,thumbnail,publishedDate,description
UCXyz123,ExampleChannel,AbC12345,My First Video,480,FALSE,12345,678,12,tech|tutorial,https...,2024-01-10T12:30:00Z,...
```

---

## ⚠️ Limitations

- Only extracts **public videos**
- Subject to **daily API quotas**
- YouTube API does not support channel discovery by niche
- Shorts detection uses **< 60 seconds** rule
- Long batch extraction may consume quota faster

---

## 🧩 Roadmap

- [ ] Automatic channel discovery by keyword
- [ ] Multithreaded API calls for faster batch mode
- [ ] Add sqlite-based local caching
- [ ] Add dedicated analytics dashboard (views/hour, growth patterns, tags analysis)
- [ ] Optional export to MongoDB / BigQuery

---

## 🤝 Contributing

Pull requests are welcome!  
If you encounter issues, feel free to open an issue in the repository.

---

## 📄 License

Distributed under the **MIT License**.  
See `LICENSE` for more information.

---

## ⭐ Support

If you found this useful, please ⭐ **star the repository** — it really helps!

