from locust import HttpUser, task, between
import uuid

class UrlShortenerUser(HttpUser):
    wait_time = between(1, 2)

    @task(3)
    def health_check(self):
        self.client.get("/health")

    @task(5)
    def create_short_link(self):
        self.client.post("/links/shorten", json={
            "original_url": f"https://example.com/{uuid.uuid4()}"
        })

    @task(1)
    def redirect(self):
        self.client.get("/test123", allow_redirects=False)
