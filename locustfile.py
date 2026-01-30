from locust import HttpUser, between, task


class APIUser(HttpUser):
    wait_time = between(1, 2)

    def on_start(self):
        # Register and login to get token
        self.email = f"test_{self.environment.runner.user_count}@example.com"
        self.password = "password123"

        # Try register
        self.client.post("/api/v1/register", json={
            "email": self.email,
            "password": self.password
        })

        # Login
        response = self.client.post("/api/v1/token", data={
            "username": self.email,
            "password": self.password
        })
        if response.status_code == 200:
            self.token = response.json()["access_token"]
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            self.token = None
            self.headers = {}

    @task(2)
    def health_check(self):
        self.client.get("/health")

    @task(1)
    def get_me(self):
        if self.token:
            self.client.get("/api/v1/users/me", headers=self.headers)
