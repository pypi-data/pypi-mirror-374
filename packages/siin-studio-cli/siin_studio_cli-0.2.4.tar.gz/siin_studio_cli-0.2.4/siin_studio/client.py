from pathlib import Path
from .calls import (
    get_all_projects_metadata,
    get_one_project_metadata,
    get_project_progress,
    filter_chunks,
    download_dataset,
    show_all_notifications,
    mark_notification_as_read,
    retrieve_project_permissions,
    get_project_team,
    ReviewStatus,
)


class Client:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.siin.studio"

    def get_all_projects_metadata(self):
        return get_all_projects_metadata(self.base_url, self.api_key)

    def get_one_project_metadata(self, project_id):
        return get_one_project_metadata(self.base_url, self.api_key, project_id)

    def get_project_progress(self, project_id):
        return get_project_progress(self.base_url, self.api_key, project_id)

    def filter_chunks(
        self, project_id, review_status: ReviewStatus = None, done: bool = None
    ):
        return filter_chunks(
            self.base_url, self.api_key, project_id, review_status, done
        )

    def download_dataset(self, project_id: str):
        output = download_dataset(self.base_url, self.api_key, project_id)
        if isinstance(output, dict):
            message = output["message"]
            print(message)
        elif isinstance(output, Path):
            print(f"Dataset downloaded to: {output.resolve()}")
            return str(output.resolve())

    def show_all_notifications(self, start=0, limit=100, only_unread=True):
        return show_all_notifications(
            self.base_url, self.api_key, start, limit, only_unread
        )

    def mark_notification_as_read(self, notification_id: str = None):
        return mark_notification_as_read(self.base_url, self.api_key, notification_id)

    def retrieve_project_permissions(self, project_id: str):
        return retrieve_project_permissions(self.base_url, self.api_key, project_id)

    def get_project_team(self, project_id: str):
        return get_project_team(self.base_url, self.api_key, project_id)
