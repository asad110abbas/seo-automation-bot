class SEOBotError(Exception):
    """Base exception for all Imp Sol errors."""
    pass


class AgentError(SEOBotError):
    def __init__(self, agent_name: str, message: str):
        self.agent_name = agent_name
        super().__init__(f"[{agent_name}] {message}")


class AgentTimeoutError(AgentError):
    pass


class CrawlError(SEOBotError):
    pass


class ExternalAPIError(SEOBotError):
    """Raised when SerpAPI, GBP API, or other external service fails."""
    def __init__(self, service: str, message: str):
        self.service = service
        super().__init__(f"[{service}] {message}")


class ProjectNotFoundError(SEOBotError):
    pass


class ReportGenerationError(SEOBotError):
    pass
