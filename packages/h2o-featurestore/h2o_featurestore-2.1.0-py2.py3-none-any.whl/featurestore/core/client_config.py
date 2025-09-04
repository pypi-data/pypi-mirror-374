class ClientConfig:
    def __init__(self, wait_for_backend: bool = True, timeout: int = 300, log_level: str = "INFO"):
        self.wait_for_backend = wait_for_backend
        self.timeout = timeout
        self.log_level = log_level
