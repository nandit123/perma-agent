# perma_agent_dashboard.py

import streamlit as st
import json
import os

METADATA_LOG_FILE = "metadata_log.json"

st.set_page_config(page_title="Lighthouse File Dashboard", layout="wide")
st.title("📦 Lighthouse Storage Dashboard")

# Load metadata records
def load_metadata():
    if not os.path.exists(METADATA_LOG_FILE):
        return []
    with open(METADATA_LOG_FILE, 'r') as f:
        lines = f.readlines()
    return [json.loads(line) for line in lines]

records = load_metadata()

if not records:
    st.info("No uploaded files found yet.")
    st.stop()

# Search bar
search_term = st.text_input("Search by filename or summary:", "")

# Filter records
filtered = [r for r in records if search_term.lower() in r["filename"].lower() or search_term.lower() in r["summary"].lower()]

# Display table
st.markdown("### Uploaded Files")
for record in filtered:
    with st.container():
        st.markdown(f"**📄 Filename:** `{record['filename']}`")
        st.markdown(f"📝 **Summary:** {record['summary']}")
        st.markdown(f"🔗 **CID:** `{record['cid']}`")
        st.markdown(f"📥 [View on IPFS](https://gateway.lighthouse.storage/ipfs/{record['cid']})")
        st.markdown(f"🕒 Uploaded: `{record['timestamp']}`")
        st.divider()

st.success(f"Showing {len(filtered)} of {len(records)} files")

