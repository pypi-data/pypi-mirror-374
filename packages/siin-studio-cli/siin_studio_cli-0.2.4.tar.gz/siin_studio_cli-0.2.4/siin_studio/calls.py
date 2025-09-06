import requests
import json
from enum import Enum
import os
from tqdm import tqdm
from pathlib import Path


class ReviewStatus(str, Enum):
    ACCEPTED = "Accepted"
    REJECTED = "Rejected"
    PENDING = "Pending"
    FEEDBACK = "Feedback"


def get_all_projects_metadata(base_url, api_key):
    endpoint = f"{base_url}/v1/multi-model"
    headers = {
        "accept": "application/json",
        "X-API-Key": api_key,
    }

    response = requests.get(endpoint, headers=headers)
    response.raise_for_status()
    return response.json()


def get_one_project_metadata(base_url, api_key, project_id):
    endpoint = f"{base_url}/v1/multi-model/{project_id}"
    headers = {
        "accept": "application/json",
        "X-API-Key": api_key,
    }

    response = requests.get(endpoint, headers=headers)
    response.raise_for_status()
    return response.json()


def get_project_progress(base_url, api_key, project_id):
    endpoint = f"{base_url}/v1/multi-model/{project_id}/progress"
    headers = {
        "accept": "application/json",
        "X-API-Key": api_key,
    }

    response = requests.get(endpoint, headers=headers)
    response.raise_for_status()
    return response.json()


def filter_chunks(
    base_url, api_key, media_id, review_status: ReviewStatus = None, done=None
):
    """
    Calls /v1/multi-model/{media_id}/filter endpoint to filter chunks.
    Args:
        base_url (str): Base API URL.
        api_key (str): API key for authentication.
        media_id (str): Media ID.
        review_status (str, optional): Review status filter.
        done (bool, optional): Done status filter.
    Returns:
        list: List of filtered chunk IDs (integers).
    """
    endpoint = f"{base_url}/v1/multi-model/{media_id}/filter"
    headers = {"accept": "application/json", "X-API-Key": api_key}
    params = {}
    if review_status is not None:
        params["review_status"] = review_status
    if done is not None:
        params["done"] = str(done).lower()
    response = requests.get(endpoint, headers=headers, params=params)
    if response.status_code >= 300:
        try:
            msg = response.json()["detail"][0]["msg"]
        except Exception:
            msg = response.json()["detail"]
        raise RuntimeError(f"Error: {msg}")
    return response.json()


def download_dataset(base_url, api_key, media_id):
    """
    Calls /v1/multi-model/dataset/{media_id} endpoint to download dataset.
    Args:
        base_url (str): Base API URL.
        api_key (str): API key for authentication.
        media_id (str): Media ID.
    Returns:
        dict: Dataset information (response JSON).
    """
    endpoint = f"{base_url}/v1/multi-model/dataset/{media_id}"
    headers = {"accept": "application/json", "X-API-Key": api_key}
    response = requests.get(endpoint, headers=headers, stream=True)
    if response.status_code >= 300:
        try:
            msg = response.json()["detail"][0]["msg"]
        except Exception:
            msg = response.text
        raise RuntimeError(f"Error: {msg}")

    content_type = response.headers.get("Content-Type", "")
    if "application/json" in content_type:
        return response.json()
    # Otherwise, treat as file (e.g., zip, csv, etc.)
    content_disp = response.headers.get("Content-Disposition", "")
    if "filename=" in content_disp:
        filename = content_disp.split("filename=")[-1].strip('"')
    else:
        filename = f"dataset_{media_id}"
    out_path = Path(filename).resolve()

    total = int(response.headers.get("content-length", 0))
    chunk_size = 8192
    with (
        out_path.open("wb") as f,
        tqdm(total=total, unit="B", unit_scale=True, desc=filename) as pbar,
    ):
        for chunk in response.iter_content(chunk_size=chunk_size):
            if chunk:
                f.write(chunk)
                pbar.update(len(chunk))
    return str(out_path)


def show_all_notifications(base_url, api_key, start=0, limit=100, only_unread=True):
    endpoint = f"{base_url}/v1/notifications"
    headers = {
        "accept": "application/json",
        "X-API-Key": api_key,
    }
    params = {
        "start": start,
        "limit": limit,
        "only_unread": only_unread,
    }

    response = requests.get(endpoint, headers=headers, params=params)
    response.raise_for_status()
    return response.json()


def mark_notification_as_read(base_url, api_key, notification_id: str = None):
    endpoint = f"{base_url}/v1/notifications/"
    headers = {
        "accept": "application/json",
        "X-API-Key": api_key,
    }
    if notification_id is None:
        # Retrieve all unread notifications and mark them as read
        all_notifications = show_all_notifications(
            base_url, api_key, start=0, limit=100, only_unread=True
        )
        unread_ids = [n["notification_id"] for n in all_notifications]
        print(f"Marking {len(unread_ids)} notifications as read...")
        for nid in unread_ids:
            mark_notification_as_read(base_url, api_key, nid)
        return
    params = {
        "notification_id": notification_id,
    }
    response = requests.patch(endpoint, headers=headers, params=params)
    response.raise_for_status()
    return response.json()


def retrieve_project_permissions(base_url, api_key, project_id):
    endpoint = f"{base_url}/v1/permissions"
    headers = {
        "accept": "application/json",
        "X-API-Key": api_key,
    }
    params = {
        "media_id": project_id,
    }
    response = requests.get(endpoint, headers=headers, params=params)
    response.raise_for_status()
    return response.json()


def get_project_team(base_url, api_key, project_id):
    endpoint = f"{base_url}/v1/permissions/team"
    headers = {
        "accept": "application/json",
        "X-API-Key": api_key,
    }
    params = {
        "media_id": project_id,
    }
    response = requests.get(endpoint, headers=headers, params=params)
    response.raise_for_status()
    return response.json()


# a = get_all_projects_metadata(
#     "https://api.siin.studio",
#     "f4e3ca1716c8ea9c6e71cd800cc72125011244b0930c0dd78bfa8a629ed44774",
# )

# a = get_one_project_metadata(
#     "https://api.siin.studio",
#     "f4e3ca1716c8ea9c6e71cd800cc72125011244b0930c0dd78bfa8a629ed44774",
#     "4abfd59b-2c90-43a0-9186-d258d7b3881e",
# )

# a = get_project_progress(
#     "https://api.siin.studio",
#     "f4e3ca1716c8ea9c6e71cd800cc72125011244b0930c0dd78bfa8a629ed44774",
#     "4abfd59b-2c90-43a0-9186-d258d7b3881e",
# )

# a = filter_chunks(
#     "https://api.siin.studio",
#     "f4e3ca1716c8ea9c6e71cd800cc72125011244b0930c0dd78bfa8a629ed44774",
#     "4abfd59b-2c90-43a0-9186-d258d7b3881e",
#     # review_status=ReviewStatus.PENDING,
#     done=False,
# )

# a = download_dataset(
#     "https://api.siin.studio",
#     "f4e3ca1716c8ea9c6e71cd800cc72125011244b0930c0dd78bfa8a629ed44774",
#     "10ced82e-3d50-4965-b488-020bd956e8c7",
# )

# a = show_all_notifications(
#     "https://api.siin.studio",
#     "f4e3ca1716c8ea9c6e71cd800cc72125011244b0930c0dd78bfa8a629ed44774",
#     start=0,
#     limit=100,
#     only_unread=True,
# )

# a = mark_notification_as_read(
#     "https://api.siin.studio",
#     "f4e3ca1716c8ea9c6e71cd800cc72125011244b0930c0dd78bfa8a629ed44774",
# )

# a = retrieve_project_permissions(
#     "https://api.siin.studio",
#     "f4e3ca1716c8ea9c6e71cd800cc72125011244b0930c0dd78bfa8a629ed44774",
#     "4abfd59b-2c90-43a0-9186-d258d7b3881e",
# )

# a = get_project_team(
#     "https://api.siin.studio",
#     "f4e3ca1716c8ea9c6e71cd800cc72125011244b0930c0dd78bfa8a629ed44774",
#     "4abfd59b-2c90-43a0-9186-d258d7b3881e",
# )
# print(json.dumps(a, indent=2))
