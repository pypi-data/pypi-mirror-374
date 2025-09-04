import pydantic


class RatesPerMillion(pydantic.BaseModel):
    input_usd: float
    output_usd: float
    cached_input_usd: float = 0.0
