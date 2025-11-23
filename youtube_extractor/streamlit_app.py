# streamlit_app.py
import os
import re
import io
import time
import pandas as pd
from datetime import datetime
import streamlit as st
from dotenv import load_dotenv
from dateutil.relativedelta import relativedelta

# import utils functions from your utils.py
# make sure utils.py is in the same directory as this app
from utils import safe_get, parse_iso_duration

# load env (optional - utils already loads but this ensures env available)
load_dotenv()

# constants
BASE = os.getenv("BASE", "https://www.googleapis.com/youtube/v3")
API_KEY = os.getenv("YT_DATA_API")

# sanity
if not API_KEY:
    st.warning("YT_DATA_API not found in environment. Make sure .env has YT_DATA_API. The app will try, but API calls will fail without a key.")

# ----------------------
# Helper wrappers (ui-friendly)
# ----------------------
def sanitize_filename(name: str) -> str:
    return re.sub(r"[^\w\-]", "", (name or "").strip())

def get_date_range_from_months(months_back: int):
    today = datetime.now()
    start = today - relativedelta(months=months_back)
    return start.strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d")

def get_uploads_playlist(channel_id: str):
    url = f"{BASE}/channels"
    params = {"part": "contentDetails,snippet", "id": channel_id, "key": API_KEY}
    data = safe_get(url, params)
    items = data.get("items", [])
    if not items:
        raise ValueError(f"Channel {channel_id} not found or API limit exceeded.")
    uploads_id = items[0]["contentDetails"]["relatedPlaylists"]["uploads"]
    channel_title = items[0]["snippet"]["title"]
    return uploads_id, channel_title

def get_all_playlist_items(playlist_id: str):
    url = f"{BASE}/playlistItems"
    videos = []
    page_token = None
    while True:
        params = {
            "part": "snippet",
            "playlistId": playlist_id,
            "maxResults": 50,
            "pageToken": page_token,
            "key": API_KEY
        }
        data = safe_get(url, params)
        for it in data.get("items", []):
            snip = it["snippet"]
            videos.append({
                "videoId": snip["resourceId"]["videoId"],
                "title": snip.get("title"),
                "publishedAt": snip.get("publishedAt"),
                "thumbnail": snip.get("thumbnails", {}).get("high", {}).get("url")
            })
        page_token = data.get("nextPageToken")
        if not page_token:
            break
    return videos

def filter_videos_by_date(videos, start_date, end_date):
    sd = datetime.fromisoformat(start_date)
    ed = datetime.fromisoformat(end_date)
    keep = []
    for v in videos:
        pub = datetime.fromisoformat(v["publishedAt"].replace("Z",""))
        if sd <= pub <= ed:
            keep.append(v)
    return keep

def fetch_videos_details(video_ids):
    url = f"{BASE}/videos"
    results = []
    for i in range(0, len(video_ids), 50):
        batch = video_ids[i:i+50]
        params = {
            "part": "snippet,statistics,contentDetails",
            "id": ",".join(batch),
            "key": API_KEY
        }
        data = safe_get(url, params)
        for item in data.get("items", []):
            snip = item.get("snippet", {})
            stats = item.get("statistics", {})
            cd = item.get("contentDetails", {})
            duration = parse_iso_duration(cd.get("duration"))
            results.append({
                "videoId": item.get("id"),
                "videoTitle": snip.get("title"),
                "description": snip.get("description"),
                "tags": "|".join(snip.get("tags", [])),
                "thumbnail": snip.get("thumbnails", {}).get("high", {}).get("url"),
                "publishedAt": snip.get("publishedAt"),
                "duration_sec": duration,
                "isShort": (duration <= 60) if (duration is not None) else False,
                "views": int(stats.get("viewCount", 0)),
                "likes": int(stats.get("likeCount", 0)) if "likeCount" in stats else None,
                "comments": int(stats.get("commentCount", 0)) if "commentCount" in stats else None
            })
    return results

def create_merged_df_from_details(details):
    df = pd.DataFrame(details)
    # ensure columns
    for c in ["videoId","videoTitle","duration_sec","isShort","views","likes","comments","tags","thumbnail","publishedAt","description","channelID","channelName"]:
        if c not in df.columns:
            df[c] = None
    df_final = pd.DataFrame({
        "channelID": df["channelID"],
        "channelName": df["channelName"],
        "videoID": df["videoId"],
        "videoTitle": df["videoTitle"],
        "duration": df["duration_sec"],
        "isShort": df["isShort"],
        "views": df["views"],
        "likes": df["likes"],
        "comments": df["comments"],
        "tags": df["tags"],
        "thumbnail": df["thumbnail"],
        "publishedDate": df["publishedAt"],
        "description": df["description"]
    })
    return df_final

# ----------------------
# UI layout
# ----------------------
st.set_page_config(page_title="YouTube Extractor", layout="wide")
st.title("YouTube Data Extractor — Streamlit")

st.markdown("Enter channel ID(s) and the months to look back. Works for single channel or batch file upload. Exports CSV(s).")

mode = st.radio("Mode", ("Single channel", "Batch from file"))

if mode == "Single channel":
    col1, col2 = st.columns([2,1])
    with col1:
        channel_id = st.text_input("Channel ID (eg. UC...)", value="")
    with col2:
        months_back = st.number_input("Months to look back", min_value=1, max_value=60, value=6, step=1)
    run_single = st.button("Run single-channel extraction")

    if run_single:
        if not channel_id.strip():
            st.error("Provide a channel ID.")
        else:
            start_date, end_date = get_date_range_from_months(months_back)
            st.info(f"Fetching videos between {start_date} and {end_date} ...")
            try:
                uploads_id, channel_name = get_uploads_playlist(channel_id.strip())
                items = get_all_playlist_items(uploads_id)
                filtered = filter_videos_by_date(items, start_date, end_date)
                if not filtered:
                    st.warning("No videos found in that range.")
                else:
                    video_ids = [v["videoId"] for v in filtered]
                    with st.spinner("Fetching video details..."):
                        details = fetch_videos_details(video_ids)
                    # add channel meta
                    for d in details:
                        d["channelID"] = channel_id.strip()
                        d["channelName"] = channel_name
                    df = create_merged_df_from_details(details)
                    st.success(f"Extracted {len(df)} videos for {channel_name}.")
                    # show first rows
                    st.dataframe(df.head(50))
                    # download
                    buf = io.BytesIO()
                    df.to_csv(buf, index=False)
                    buf.seek(0)
                    fname = f"{sanitize_filename(channel_name)}{len(df)}.csv"
                    st.download_button("Download CSV", data=buf, file_name=fname, mime="text/csv")
            except Exception as e:
                st.error(f"Error: {e}")

else:  # Batch mode
    st.info("Upload a text file (one channel ID per line) or paste list below.")
    uploaded = st.file_uploader("Upload channel-id file (.txt)", type=["txt"])
    pasted = st.text_area("Or paste channel IDs (one per line)", value="", height=240)
    months_back_batch = st.number_input("Months to look back (batch)", min_value=1, max_value=60, value=6, step=1)
    category_label = st.text_input("Output category label (used only in filename)", value="my_category")
    run_batch = st.button("Run batch extraction")

    if run_batch:
        # prepare list
        ids = []
        if uploaded is not None:
            try:
                text = uploaded.getvalue().decode("utf-8")
                ids += [l.strip() for l in text.splitlines() if l.strip()]
            except Exception as e:
                st.error(f"Failed to read uploaded file: {e}")
                ids = []
        if pasted.strip():
            ids += [l.strip() for l in pasted.splitlines() if l.strip()]
        # unique
        ids = list(dict.fromkeys(ids))
        if not ids:
            st.error("No channel IDs provided.")
        else:
            start_date, end_date = get_date_range_from_months(months_back_batch)
            st.info(f"Fetching videos between {start_date} and {end_date} for {len(ids)} channels...")

            all_results = []
            progress = st.progress(0)
            status_text = st.empty()
            for idx, cid in enumerate(ids, start=1):
                status_text.text(f"Processing {idx}/{len(ids)} — {cid}")
                try:
                    uploads_id, channel_name = get_uploads_playlist(cid)
                    items = get_all_playlist_items(uploads_id)
                    filtered = filter_videos_by_date(items, start_date, end_date)
                    if not filtered:
                        status_text.text(f"No videos in range for {cid} — skipping")
                    else:
                        ids_batch = [v["videoId"] for v in filtered]
                        details = fetch_videos_details(ids_batch)
                        for d in details:
                            d["channelID"] = cid
                            d["channelName"] = channel_name
                        all_results.extend(details)
                        status_text.text(f"Added {len(details)} videos for {channel_name}")
                except Exception as e:
                    status_text.text(f"Error for {cid}: {e}")
                progress.progress(int(idx/len(ids) * 100))
                time.sleep(0.1)  # small throttle so UI updates

            if not all_results:
                st.warning("No videos extracted from any channel.")
            else:
                df = create_merged_df_from_details(all_results)
                st.success(f"Batch extraction finished. Total videos: {len(df)}")
                st.dataframe(df.head(100))
                # save to disk (optional)
                os.makedirs("output", exist_ok=True)
                sanitized_label = sanitize_filename(category_label or "category")
                out_path = f"output/yt_data_{sanitized_label}.csv"
                df.to_csv(out_path, index=False)
                st.write(f"Saved file to `{out_path}`")
                # offer download
                buf = io.BytesIO()
                df.to_csv(buf, index=False)
                buf.seek(0)
                st.download_button("Download merged CSV", data=buf, file_name=f"yt_data_{sanitized_label}.csv", mime="text/csv")

st.markdown("---")
st.markdown("Tip: If your `.env` is not loaded, make sure `YT_DATA_API` is set. Keep `utils.py` next to this file.")
