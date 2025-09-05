import json

from ..models import CourseInstance


class JSONWriter:
    """Writer class for JSON output with consistent interface."""

    def __init__(self, filename: str | None = None):
        self.filename = filename
        self.schedules: list[list[dict]] = []

    def __enter__(self):
        return self

    def add_schedule(self, schedule: list[CourseInstance]) -> None:
        """Add a schedule to be written."""

        schedule_data = [course_instance.as_json() for course_instance in schedule]
        if self.filename:
            self.schedules.append(schedule_data)
        else:
            print(json.dumps(schedule_data, separators=(",", ":")))

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        """Write all accumulated schedules as one JSON array."""
        if self.filename:
            content = json.dumps(self.schedules, separators=(",", ":"))
            with open(self.filename, "w", encoding="utf-8") as f:
                f.write(content)
