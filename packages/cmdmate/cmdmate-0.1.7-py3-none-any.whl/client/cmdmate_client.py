import warnings
from urllib3.exceptions import NotOpenSSLWarning

warnings.simplefilter("ignore", NotOpenSSLWarning)

import platform
import requests

from .cmdmate_apiClient import ApiClient

class CmdmateClient:
    def __init__(self, server_url="https://cmdmate-online.onrender.com/"):
        self.api = ApiClient(server_url)

    @staticmethod
    def detect_os() -> str:
        system = platform.system().lower()
        if system == "darwin":
            return "mac"
        elif system == "linux":
            return "linux"
        elif system == "windows":
            return "windows"
        else:
            return "unknown"

    def get_command(self, query: str, os_name: str = None) -> str:
        if not os_name:
            os_name = self.detect_os()

        data = self.api.post("/getCmd", {"text": query, "os": os_name})
        return data.get("command", "")

    def get_explanation(self, query: str) -> str:
        data = self.api.post("/getExplaination", {"text": query})
        return data.get("explanation", "")

    def get_commitMsg(self, diff_input: str) -> str:
        data = self.api.post("/getCommitMsg", {"text": diff_input})
        return data.get("commit_message", "")
    
    def get_response_from_input(self, input: str, query: str) -> str:
        data = self.api.post("/getResponseFromInput", {"input": input, "query": query})
        return data.get("response", "")