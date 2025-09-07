import os
from abc import ABC
from typing import Callable


class SparkdenWorker(ABC):
    def __init__(
        self,
        on_broker_ready: Callable,
    ):
        self.setup_environment()
        self.setup_broker()
        self.setup_queued_jobs()

        on_broker_ready()

    def setup_environment(self):
        """
        Load environment variables and configure API keys.
        """
        import dashscope
        from dotenv import find_dotenv, load_dotenv

        dotenv_path = find_dotenv(usecwd=True)
        load_dotenv(dotenv_path)
        dashscope.api_key = os.environ.get("DASHSCOPE_API_KEY")

    def setup_broker(self):
        """
        Setup broker.
        """
        import dramatiq

        from .broker import create_broker

        self.broker = create_broker()
        dramatiq.set_broker(self.broker)

    def setup_queued_jobs(self):
        """
        Setup job functions.
        """
        import sparkden.queued_job.data_source_job  # noqa: F401
