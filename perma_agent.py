# perma_agent.py

import os
import time
import json
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from langchain_openai import OpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_unstructured import UnstructuredLoader
from langchain.text_splitter import CharacterTextSplitter
import requests
from dotenv import load_dotenv

load_dotenv()

LIGHTHOUSE_API_URL = "https://node.lighthouse.storage/api/v0/add"
LIGHTHOUSE_API_KEY = os.getenv("LIGHTHOUSE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

FAILED_LOG_FILE = "failed_uploads.json"
METADATA_LOG_FILE = "metadata_log.json"

class FileHandler(FileSystemEventHandler):
    def __init__(self, llm):
        self.llm = llm
        self.db = None
        self.embedding_fn = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)

    def process_file(self, file_path):
        filename = os.path.basename(file_path)

        if filename.startswith('.') or filename.endswith(('.DS_Store', '.png', '.jpg', '.zip', '.exe', '.pdf', '.bin')):
            print(f"Skipping unsupported file: {filename}")
            return

        print(f"Processing new file: {file_path}")
        summary = ""

        try:
            loader = UnstructuredLoader(file_path)
            docs = loader.load()
            splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
            docs = splitter.split_documents(docs)

            if self.db is None:
                self.db = FAISS.from_documents(docs, self.embedding_fn)
            else:
                self.db.add_documents(docs)

            file_content = open(file_path, 'r', errors='ignore').read()[:3000]
            summary_prompt = f"Summarize this file: {file_content}"
            summary = self.llm.invoke(summary_prompt)
            print(f"Summary: {summary}")
        except Exception as e:
            print(f"Error processing file content: {e}")
            self.log_failure(filename, str(e))
            return

        try:
            files = {"file": open(file_path, "rb")}
            headers = {"Authorization": f"Bearer {LIGHTHOUSE_API_KEY}"}
            res = requests.post(LIGHTHOUSE_API_URL, headers=headers, files=files)
            if res.status_code == 200:
                cid = res.json().get("Hash")
                print(f"Uploaded to Lighthouse: {res.json()}")
                self.log_metadata(filename, cid, summary)
            else:
                print(f"Upload failed: {res.status_code} - {res.text}")
                self.log_failure(filename, f"Upload failed: {res.status_code}")
        except Exception as e:
            print(f"Error uploading to Lighthouse: {e}")
            self.log_failure(filename, str(e))

    def log_failure(self, filename, error):
        record = {"filename": filename, "error": error, "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")}
        with open(FAILED_LOG_FILE, 'a') as f:
            f.write(json.dumps(record) + "\n")

    def log_metadata(self, filename, cid, summary):
        record = {
            "filename": filename,
            "cid": cid,
            "summary": summary,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        with open(METADATA_LOG_FILE, 'a') as f:
            f.write(json.dumps(record) + "\n")

    def on_created(self, event):
        if not event.is_directory:
            self.process_file(event.src_path)

def start_monitor(path):
    print(f"Monitoring folder: {path}")
    llm = OpenAI(model_name="gpt-3.5-turbo-instruct", temperature=0, openai_api_key=OPENAI_API_KEY)
    event_handler = FileHandler(llm)
    observer = Observer()
    observer.schedule(event_handler, path, recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    folder_to_monitor = "./watched_folder"
    os.makedirs(folder_to_monitor, exist_ok=True)
    start_monitor(folder_to_monitor)
