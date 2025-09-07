class SharepointError(Exception):
    """Raised when acquiring a SharePoint access token fails."""

    def __init__(self, message: str, details: dict | None = None):
        self.details = details or {}
        super().__init__(message)