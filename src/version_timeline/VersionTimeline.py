from datetime import datetime

class VersionTimeline:

    timeline = []

    def create_timestamp(self):
        timestamp = f"ts{datetime.now().strftime("%Y%m%d%H%M%S")}"
        self.timeline.append(timestamp)
        return timestamp

    def get_latest_timestamp(self):
        return self.timeline[-1]
    
