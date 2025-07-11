import time
from locust import task, between
from locust.contrib.fasthttp import FastHttpUser
import json

class WebsiteUser(FastHttpUser):
    """
    Simulates a user interacting with the simulation API.
    Focuses on HTTP endpoints for robustness.
    """
    wait_time = between(1, 3)
    connection_timeout = 30
    network_timeout = 30

    @task(1)
    def start_and_get_state(self):
        """Task to start the simulation and fetch its initial state."""
        # Renamed to the correct endpoint
        self.client.get("/api/world_state")

    @task(5)
    def get_statistics(self):
        """Task to frequently poll the statistics endpoint."""
        self.client.get("/api/statistics")

    @task(2)
    def get_full_state(self):
        """Task to occasionally request the full state of the simulation."""
        # Renamed to the correct endpoint and removed query params
        self.client.get("/api/world_state")

    def on_start(self):
        """
        on_start is called when a Locust start before any task is scheduled.
        You can add login or setup logic here.
        """
        # For example, ensure the server is ready.
        # This initial request can also serve to "wake up" the server.
        self.client.get("/api/statistics") 