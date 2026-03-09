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

    @task(2)
    def get_stats(self):
        short_code = "test123"
        self.client.get(f"/links/{short_code}/stats")

    @task(1)
    def redirect(self):
        short_code = "test123"
        self.client.get(f"/{short_code}", allow_redirects=False)
