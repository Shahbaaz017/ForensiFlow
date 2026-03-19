import abc
import json
import logging

class BaseWorker(metaclass=abc.ABCMeta):
    """
    All forensic workers MUST inherit from this BaseWorker.
    This ensures consistency across the ForensiFlow framework.
    """

    @abc.abstractmethod
    def run(self, evidence_path: str) -> dict:
        """
        Each worker must implement this method.
        It should return a standardized dictionary (JSON-ready).
        """
        pass

    def create_result(self, worker_name: str, status: str, findings: dict = None, errors: str = None):
        """
        A helper method to ensure every tool returns the same JSON structure.
        """
        return {
            "worker": worker_name,
            "status": status,
            "findings": findings if findings else {},
            "errors": errors if errors else None
        }

    def log(self, message: str):
        """Helper to log actions to the console/file."""
        logging.info(f"[{self.__class__.__name__}] {message}")