import json
import random
import uuid
import pathlib

from locust import HttpUser, task, between, events


SAMPLE_PHOTO_PATH = pathlib.Path(__file__).parent / "apple.jpg"


@events.request.add_listener
def validate_json_response(request_type, name, response, **kwargs):
    if response.status_code >= 400:
        return

    try:
        response.json()
    except (json.JSONDecodeError, ValueError) as e:
        response.failure(f"Invalid JSON response: {e}")


HEADERS = {
    "Accept": "application/json",
}


class PhotoGalleryUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        """Register one user per simulated user so login can succeed."""
        self.username = f"loadtest_{uuid.uuid4().hex[:12]}"
        self.password = "testpass123"
        self.uploaded_photo_ids = []
        self.client.post(
            "/auth/register",
            data={"username": self.username, "password": self.password},
            headers=HEADERS,
        )

    @task(3)
    def view_homepage(self):
        self.client.get("/", headers=HEADERS)

    @task(2)
    def view_photos_sorted_by_name(self):
        self.client.get("/?sort=name", headers=HEADERS)

    @task(2)
    def view_photos_sorted_by_date(self):
        self.client.get("/?sort=date", headers=HEADERS)

    @task(1)
    def login(self):
        self.client.post(
            "/auth/login",
            data={"username": self.username, "password": self.password},
            headers=HEADERS,
        )

    @task(2)
    def upload_photo(self):
        with open(SAMPLE_PHOTO_PATH, "rb") as f:
            response = self.client.post(
                "/upload",
                data={"name": f"Test Photo {uuid.uuid4().hex[:12]}"},
                files={"file": ("apple.jpg", f, "image/jpeg")},
                headers=HEADERS,
            )
        if response.status_code == 200:
            data = response.json()
            if "photo_id" in data:
                self.uploaded_photo_ids.append(data["photo_id"])

    @task(2)
    def view_photo_detail(self):
        if not self.uploaded_photo_ids:
            return
        photo_id = random.choice(self.uploaded_photo_ids)
        self.client.get(f"/photo/{photo_id}", headers=HEADERS)

    @task(1)
    def delete_photo(self):
        if not self.uploaded_photo_ids:
            return
        photo_id = random.choice(self.uploaded_photo_ids)
        self.client.delete(f"/photo/{photo_id}/delete", headers=HEADERS)
        self.uploaded_photo_ids.remove(photo_id)
