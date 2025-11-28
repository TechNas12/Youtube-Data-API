import os
import re
import io
import time
import zipfile
import pandas as pd
from datetime import datetime
import streamlit as st
from dotenv import load_dotenv
from dateutil.relativedelta import relativedelta

from utils import safe_get, parse_iso_duration

load_dotenv()

BASE = os.getenv("BASE", "https://www.googleapis.com/youtube/v3")
API_KEY = os.getenv("YT_DATA_API")

if not API_KEY:
    st.warning("YT_DATA_API missing from .env — API calls will fail.")


# ============================================================
# UTILS
# ============================================================
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
        raise ValueError(f"Channel {channel_id} not found.")

    uploads_id = items[0]["contentDetails"]["relatedPlaylists"]["uploads"]
    channel_title = items[0]["snippet"]["title"]
    return uploads_id, channel_title


def get_channel_stats(channel_id: str):
    url = f"{BASE}/channels"
    params = {"part": "statistics,snippet", "id": channel_id, "key": API_KEY}
    data = safe_get(url, params)

    items = data.get("items", [])
    if not items:
        raise ValueError(f"Stats not found for channel {channel_id}")

    stats = items[0]["statistics"]
    snippet = items[0]["snippet"]

    # subscriber count may be hidden
    subs = None
    if not stats.get("hiddenSubscriberCount"):
        subs = int(stats.get("subscriberCount", 0))

    return {
        "channelID": channel_id,
        "channelName": snippet.get("title"),
        "subscribers": subs,
        "totalViews": int(stats.get("viewCount", 0)),
        "totalVideos": int(stats.get("videoCount", 0)),
    }


def get_all_playlist_items(playlist_id: str):
    url = f"{BASE}/playlistItems"
    out = []
    page = None

    while True:
        params = {
            "part": "snippet",
            "playlistId": playlist_id,
            "maxResults": 50,
            "pageToken": page,
            "key": API_KEY,
        }
        data = safe_get(url, params)

        for it in data.get("items", []):
            sn = it["snippet"]
            out.append({
                "videoId": sn["resourceId"]["videoId"],
                "title": sn.get("title"),
                "publishedAt": sn.get("publishedAt"),
                "thumbnail": sn.get("thumbnails", {}).get("high", {}).get("url"),
            })

        page = data.get("nextPageToken")
        if not page:
            break

    return out


def filter_videos_by_date(videos, start, end):
    sd = datetime.fromisoformat(start)
    ed = datetime.fromisoformat(end)
    keep = []
    for v in videos:
        pub = datetime.fromisoformat(v["publishedAt"].replace("Z",""))
        if sd <= pub <= ed:
            keep.append(v)
    return keep


def fetch_videos_details(video_ids):
    url = f"{BASE}/videos"
    out = []

    for i in range(0, len(video_ids), 50):
        batch = video_ids[i:i+50]
        params = {
            "part": "snippet,statistics,contentDetails",
            "id": ",".join(batch),
            "key": API_KEY
        }
        data = safe_get(url, params)

        for it in data.get("items", []):
            sn = it.get("snippet", {})
            stt = it.get("statistics", {})
            cd  = it.get("contentDetails", {})

            duration = parse_iso_duration(cd.get("duration"))
            out.append({
                "videoId": it.get("id"),
                "videoTitle": sn.get("title"),
                "description": sn.get("description"),
                "tags": "|".join(sn.get("tags", [])),
                "thumbnail": sn.get("thumbnails", {}).get("high", {}).get("url"),
                "publishedAt": sn.get("publishedAt"),
                "duration_sec": duration,
                "isShort": duration <= 60 if duration else False,
                "views": int(stt.get("viewCount", 0)),
                "likes": int(stt.get("likeCount", 0)) if "likeCount" in stt else None,
                "comments": int(stt.get("commentCount", 0)) if "commentCount" in stt else None,
            })

    return out


def build_video_df(details):
    df = pd.DataFrame(details)

    needed = [
        "channelID","channelName","videoId","videoTitle","duration_sec",
        "isShort","views","likes","comments","tags","thumbnail","publishedAt","description"
    ]
    for col in needed:
        if col not in df.columns:
            df[col] = None

    return pd.DataFrame({
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
        "description": df["description"],
    })


# ============================================================
# ZIP CREATION
# ============================================================
def create_zip(videos_df, stats_df):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zf:
        zf.writestr("yt_data_videos.csv", videos_df.to_csv(index=False))
        zf.writestr("yt_data_stats.csv", stats_df.to_csv(index=False))

    zip_buffer.seek(0)
    return zip_buffer


# ============================================================
# UI SETUP
# ============================================================
st.set_page_config(page_title="YouTube Extractor", layout="wide")
st.title("YouTube Data Extractor — Streamlit (ZIP Output)")
st.markdown("Extract video-level + channel-level CSVs packaged into **yt_data.zip**")


mode = st.radio("Mode", ["Single channel", "Batch from file"])


# ============================================================
# SINGLE CHANNEL MODE
# ============================================================
if mode == "Single channel":
    col1, col2 = st.columns([2,1])

    with col1:
        channel_id = st.text_input("Channel ID (UC...)", "")
    with col2:
        months_back = st.number_input("Months to look back", 1, 60, 6)

    if st.button("Run extraction"):
        if not channel_id.strip():
            st.error("Enter a channel ID.")
        else:
            start, end = get_date_range_from_months(months_back)
            st.info(f"Fetching videos between {start} and {end}...")

            try:
                uploads_id, channel_name = get_uploads_playlist(channel_id)
                stats = get_channel_stats(channel_id)

                all_items = get_all_playlist_items(uploads_id)
                filtered = filter_videos_by_date(all_items, start, end)

                # Build stats row
                stats_row = {
                    "channelID": channel_id,
                    "channelName": channel_name,
                    "subscribers": stats["subscribers"],
                    "totalViews": stats["totalViews"],
                    "totalVideos": stats["totalVideos"],
                    "videosInRange": len(filtered),
                    "extractedAt": datetime.now().isoformat()
                }

                df_stats = pd.DataFrame([stats_row])

                if len(filtered) == 0:
                    st.warning("No videos in the selected time range.")

                    # Still create the ZIP with empty video CSV
                    empty_df = pd.DataFrame(columns=[
                        "channelID","channelName","videoID","videoTitle","duration",
                        "isShort","views","likes","comments","tags","thumbnail","publishedDate","description"
                    ])
                    zip_data = create_zip(empty_df, df_stats)

                    st.download_button("Download yt_data.zip", zip_data,
                        file_name="yt_data.zip", mime="application/zip")
                else:
                    ids = [v["videoId"] for v in filtered]
                    details = fetch_videos_details(ids)

                    for d in details:
                        d["channelID"] = channel_id
                        d["channelName"] = channel_name

                    df_videos = build_video_df(details)

                    st.success(f"Extracted {len(df_videos)} videos.")
                    st.dataframe(df_videos.head())

                    # ZIP output
                    zip_data = create_zip(df_videos, df_stats)

                    st.download_button("Download yt_data.zip", zip_data,
                        file_name="yt_data.zip", mime="application/zip")

            except Exception as e:
                st.error(str(e))



# ============================================================
# BATCH MODE
# ============================================================
else:
    st.info("Upload .txt file or paste channel IDs (one per line).")

    file = st.file_uploader("Upload TXT (channel IDs)", type=["txt"])
    pasted = st.text_area("Or paste channel IDs", height=200)
    months_back = st.number_input("Months to look back", 1, 60, 6)

    if st.button("Run batch extraction"):
        ids = []

        if file:
            text = file.read().decode("utf-8")
            ids += [x.strip() for x in text.splitlines() if x.strip()]

        if pasted.strip():
            ids += [x.strip() for x in pasted.splitlines() if x.strip()]

        ids = list(dict.fromkeys(ids))  # unique

        if not ids:
            st.error("No channel IDs found.")
        else:
            start, end = get_date_range_from_months(months_back)
            st.info(f"Processing {len(ids)} channels...")

            all_video_details = []
            stats_rows = []

            progress = st.progress(0)
            status = st.empty()

            for i, cid in enumerate(ids, start=1):
                status.text(f"Processing {cid} ({i}/{len(ids)})")

                try:
                    uploads_id, cname = get_uploads_playlist(cid)
                    stats = get_channel_stats(cid)

                    all_items = get_all_playlist_items(uploads_id)
                    filtered = filter_videos_by_date(all_items, start, end)

                    # Stats entry
                    stats_rows.append({
                        "channelID": cid,
                        "channelName": cname,
                        "subscribers": stats["subscribers"],
                        "totalViews": stats["totalViews"],
                        "totalVideos": stats["totalVideos"],
                        "videosInRange": len(filtered),
                        "extractedAt": datetime.now().isoformat()
                    })

                    if filtered:
                        ids_batch = [v["videoId"] for v in filtered]
                        details = fetch_videos_details(ids_batch)

                        for d in details:
                            d["channelID"] = cid
                            d["channelName"] = cname

                        all_video_details.extend(details)

                except Exception as e:
                    status.text(f"Error for {cid}: {e}")

                progress.progress(i / len(ids))

            # assemble dataframes
            df_stats = pd.DataFrame(stats_rows)

            df_videos = (
                build_video_df(all_video_details)
                if all_video_details else
                pd.DataFrame(columns=[
                    "channelID","channelName","videoID","videoTitle","duration","isShort",
                    "views","likes","comments","tags","thumbnail","publishedDate","description"
                ])
            )

            st.success("Batch extraction finished.")
            st.dataframe(df_stats.head())

            # ZIP output
            zip_data = create_zip(df_videos, df_stats)

            st.download_button(
                "Download yt_data.zip",
                zip_data,
                file_name="yt_data.zip",
                mime="application/zip"
            )


st.markdown("---")
st.markdown("Ensure `.env` contains `YT_DATA_API`. Keep `utils.py` in the same folder.")
