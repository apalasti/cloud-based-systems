import uuid

from locust import HttpUser, task, between

FORM_HEADERS = {"Content-Type": "application/x-www-form-urlencoded"}


class PhotoGalleryUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        """Register one user per simulated user so login can succeed."""
        self.username = f"loadtest_{uuid.uuid4().hex[:12]}"
        self.password = "testpass123"
        self.client.post(
            "/auth/register",
            data={"username": self.username, "password": self.password},
            headers=FORM_HEADERS,
        )

    @task(3)
    def view_homepage(self):
        self.client.get("/")

    @task(2)
    def view_photos_sorted_by_name(self):
        self.client.get("/?sort=name")

    @task(2)
    def view_photos_sorted_by_date(self):
        self.client.get("/?sort=date")

    @task(1)
    def view_login_page(self):
        self.client.post(
            "/auth/login",
            data={"username": self.username, "password": self.password},
            headers=FORM_HEADERS,
        )

    @task(2)
    def view_register_page(self):
        username = f"loadtest_{uuid.uuid4().hex[:12]}"
        password = "testpass123"
        self.client.post(
            "/auth/register",
            data={"username": username, "password": password},
            headers=FORM_HEADERS,
        )
