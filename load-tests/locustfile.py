from locust import HttpUser, between, task


class Shopper(HttpUser):
    wait_time = between(0.1, 0.5)

    @task(4)
    def list_orders(self):
        self.client.get("/api/orders", name="/api/orders")

    @task(1)
    def home(self):
        self.client.get("/", name="/")
