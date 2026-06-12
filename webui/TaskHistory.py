import os
import sys
from datetime import datetime

import streamlit as st

from loguru import logger

import requests

root_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if root_dir not in sys.path:
    sys.path.append(root_dir)

from app.config import config
from app.models import const
from app.utils import utils

# API base URL
API_BASE = config.app.get("endpoint", "") or f"http://127.0.0.1:8080"

st.set_page_config(
    page_title="AI Video Workshop - Task History",
    page_icon="📋",
    layout="wide",
)

st.title("📋 Video Task History")
st.markdown("---")

# Fetch all tasks
def fetch_tasks():
    """Fetch task list from the API server"""
    try:
        resp = requests.get(f"{API_BASE}/api/v1/tasks", timeout=10)
        if resp.status_code == 200:
            data = resp.json().get("data", {})
            return data.get("tasks", [])
    except Exception as e:
        logger.error(f"Failed to fetch tasks: {e}")
        return []

# Fetch single task detail
def fetch_task_detail(task_id):
    """Fetch task detail from the API server"""
    try:
        resp = requests.get(f"{API_BASE}/api/v1/tasks/{task_id}", timeout=10)
        if resp.status_code == 200:
            return resp.json().get("data", {})
    except Exception as e:
        logger.error(f"Failed to fetch task detail: {e}")
        return {}

# State display mapping
STATE_MAP = {
    const.TASK_STATE_FAILED: ("❌ Failed", "red"),
    const.TASK_STATE_COMPLETE: ("✅ Completed", "green"),
    const.TASK_STATE_PROCESSING: ("🔄 Processing", "orange"),
}

def state_badge(state):
    label, color = STATE_MAP.get(state, ("⏳ Unknown", "gray"))
    return label, color

# Load tasks
tasks = fetch_tasks()

if not tasks:
    st.info("No tasks found. Create a video first from the main page!")
    st.stop()

st.markdown(f"**Total tasks: {len(tasks)}**")

# Display tasks in a table-like layout
for task in reversed(tasks):  # Show newest first
    task_id = task.get("task_id", "")
    state = task.get("state", 0)
    progress = task.get("progress", 0)
    script = task.get("script", "")
    videos = task.get("videos", [])
    
    label, color = state_badge(state)
    
    # Create a card for each task
    with st.container(border=True):
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            # Show script preview (truncated)
            if script:
                preview = script[:100] + "..." if len(script) > 100 else script
                st.markdown(f"**📝 {preview}**")
            else:
                st.markdown("**📝 No script**")
            
            # Show video link if completed
            if state == const.TASK_STATE_COMPLETE and videos:
                for video_path in videos:
                    # Convert server path to URL path
                    video_filename = os.path.basename(video_path)
                    video_url = f"{API_BASE}/tasks/{task_id}/{video_filename}"
                    st.video(video_url)
                    st.markdown(f"[⬇️ Download Video]({video_url})")
        
        with col2:
            st.markdown(f":{color}[**{label}**]")
            if progress > 0:
                st.progress(progress / 100)
        
        with col3:
            st.caption(f"ID: `{task_id}`")
            # Show task terms if available
            terms = task.get("terms", "")
            if terms and terms != "Error":
                if isinstance(terms, list):
                    st.caption(f"Keywords: {', '.join(terms[:5])}")
                elif isinstance(terms, str):
                    st.caption(f"Keywords: {terms[:80]}")

# Auto-refresh option
st.markdown("---")
auto_refresh = st.checkbox("Auto-refresh every 5 seconds", value=False)
if auto_refresh:
    st.markdown("🔄 Auto-refreshing...")
    import time
    time.sleep(5)
    st.rerun()