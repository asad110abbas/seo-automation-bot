from groq import Groq
from tenacity import retry, stop_after_attempt, wait_exponential
from app.config import settings

# Groq llama-3.3-70b-versatile pricing (USD per 1M tokens)
_INPUT_COST_PER_M = 0.59
_OUTPUT_COST_PER_M = 0.79


class TokenUsage:
    def __init__(self):
        self.input_tokens = 0
        self.output_tokens = 0

    @property
    def input_cost(self) -> float:
        return (self.input_tokens / 1_000_000) * _INPUT_COST_PER_M

    @property
    def output_cost(self) -> float:
        return (self.output_tokens / 1_000_000) * _OUTPUT_COST_PER_M

    @property
    def total_cost(self) -> float:
        return self.input_cost + self.output_cost

    def add(self, input_t: int, output_t: int):
        self.input_tokens += input_t
        self.output_tokens += output_t


class ClaudeClient:
    def __init__(self):
        self.client = Groq(api_key=settings.groq_api_key)
        self.model = settings.groq_model
        self.usage = TokenUsage()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=30))
    def analyze(self, system_prompt: str, user_content: str, max_tokens: int = 4096) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            max_tokens=max_tokens,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
        )
        if response.usage:
            self.usage.add(response.usage.prompt_tokens, response.usage.completion_tokens)
        return response.choices[0].message.content

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=30))
    def stream(self, system_prompt: str, user_content: str, max_tokens: int = 8192):
        stream = self.client.chat.completions.create(
            model=self.model,
            max_tokens=max_tokens,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
            stream=True,
        )
        for chunk in stream:
            content = chunk.choices[0].delta.content
            if content:
                yield content

    def reset_usage(self):
        self.usage = TokenUsage()


_llm_client: ClaudeClient | None = None


def get_claude() -> ClaudeClient:
    global _llm_client
    if _llm_client is None:
        _llm_client = ClaudeClient()
    return _llm_client
