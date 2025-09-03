from version_timeline.VersionTimeline import VersionTimeline
import json

version_timeline = VersionTimeline()

def log_timeline(project_id: str):
    print(json.dumps(version_timeline.timeline[project_id], indent=4))