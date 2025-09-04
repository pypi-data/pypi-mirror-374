import models

CACHE_FOLDER = './.cache'
MODEL_RATES = {
    'gpt-5-nano': models.RatesPerMillion(input_usd=0.05, output_usd=0.40, cached_input_usd=0.005),
}
