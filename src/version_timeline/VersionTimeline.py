from datetime import datetime
import os
import json
from neo4j_core.neo4j_model import PrimaryNode

class VersionTimeline:

    def __init__(self):
        os.makedirs("./timeline_data", exist_ok=True)
        if os.path.exists("./timeline_data/timeline.json"):
            with open("./timeline_data/timeline.json", "r") as f:
                self.timeline = json.load(f)
        else:
            self.timeline = {}

    def save(self):
        os.makedirs("./timeline_data", exist_ok=True)
        with open("./timeline_data/timeline.json", "w") as f:
            json.dump(self.timeline, f, indent=4)

    def add_commit_to_timeline(self, timestamp: str):
        project_id = PrimaryNode.nodes.get(timestamp=timestamp, EntityType="IfcProject").GlobalId
        if project_id not in self.timeline:
            self.timeline[project_id] = []
        self.timeline[project_id].append(timestamp)

    def get_latest_commit_timestamp(self, timestamp: str):
        project_id = PrimaryNode.nodes.get(timestamp=timestamp, EntityType="IfcProject").GlobalId
        if project_id in self.timeline and self.timeline[project_id]:
            return self.timeline[project_id][-1]
        else:
            return None

    @staticmethod
    def create_timestamp():
        timestamp = f"ts{datetime.now().strftime('%Y%m%d%H%M%S')}"
        return timestamp