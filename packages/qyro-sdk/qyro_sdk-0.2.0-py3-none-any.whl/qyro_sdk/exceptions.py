class QyroError(Exception):
    """Base SDK error"""


class HTTPError(QyroError):
    def __init__(self, status_code, message, response=None):
        super().__init__(f"HTTP {status_code}: {message}")
        self.status_code = status_code
        self.response = response


class ConfigurationError(QyroError):
    pass
