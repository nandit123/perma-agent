# 🧠 Perma Agent – AI-Powered File Backup & Metadata on Lighthouse

This tool automatically watches a folder, summarizes new files using GPT, uploads them to Lighthouse, and logs metadata. Includes a Streamlit dashboard to search and view uploads.

## 🚀 Features
- Auto-upload files to Lighthouse.Storage
- GPT-generated summaries
- Stores metadata in JSON
- Streamlit dashboard for easy viewing
- Skips non-readable/binary files

## 🔧 Setup

```bash
git clone https://github.com/yourname/perma-agent.git
cd perma-agent
pip3 install -r requirements.txt
cp .env.example .env

### Run the agent
`python perma_agent.py`

### Run the dashboard
`streamlit run perma_agent_dashboard.py`
