from datetime import datetime
import os
import json  # Changed from pickle to json

class VersionTimeline:

    def __init__(self, timeline_path="./timeline_data/timeline.json"):
        self.timeline_path = timeline_path
        self.timeline = []
        self.load()

    def load(self):
        if os.path.exists(self.timeline_path):
            try:
                with open(self.timeline_path, "r") as f:
                    self.timeline = json.load(f)  # Load from JSON
            except FileNotFoundError:
                print(f"Timeline file not found at {self.timeline_path}. Initializing empty timeline.")
                self.timeline = []
            except json.JSONDecodeError:
                print(f"Error decoding JSON from {self.timeline_path}. Initializing empty timeline.")
                self.timeline = []
        else:
            self.timeline = []
            print(f"Timeline file not found at {self.timeline_path}. Initializing empty timeline.")

    def save(self):
        os.makedirs(os.path.dirname(self.timeline_path), exist_ok=True)
        with open(self.timeline_path, "w") as f:
            json.dump(self.timeline, f, indent=4)  # Save to JSON with indentation

    def add_commit_to_timeline(self, timestamp: str):
        self.timeline.append(timestamp)

    def get_latest_commit_timestamp(self):
        if self.timeline:
            return self.timeline[-1]
        else:
            return None  # Or raise an exception

    @staticmethod
    def create_timestamp():
        timestamp = f"ts{datetime.now().strftime('%Y%m%d%H%M%S')}"
        return timestamp