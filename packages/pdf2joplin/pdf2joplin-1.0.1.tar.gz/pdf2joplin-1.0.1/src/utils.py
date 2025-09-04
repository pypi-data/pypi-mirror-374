import os
import base64

import constants


def print_banner() -> None:
    banner = r"""
 ____  ____  ____  ___   __  __  ____  
(  _ \(  _ \( ___)(__ \ (  \/  )(  _ \ 
 )___/ )(_) ))__)  / _/  )    (  )(_) )
(__)  (____/(__)  (____)(_/\/\_)(____/ 
"""

    print(banner)


def create_folder(folderpath: str) -> None:
    if not os.path.exists(folderpath):
        os.makedirs(folderpath)


def clear_folder(folderpath: str) -> None:
    for filename in os.listdir(folderpath):
        os.remove(os.path.join(folderpath, filename))


def delete_file(filepath: str) -> None:
    if os.path.isfile(filepath):
        os.remove(filepath)


def img_to_base64(imagepath: str) -> str:
    with open(imagepath, 'rb') as img_file:
        encoded = base64.b64encode(img_file.read())
        return encoded.decode('utf-8')


def append_to_file(filepath: str, text: str) -> None:
    with open(filepath, 'a', encoding='utf-8') as f:
        f.write(text)


def calculate_openai_costs(responses: list) -> float:
    total_cost = 0.0

    for resp in responses:
        rates = constants.MODEL_RATE
        usage = getattr(resp, 'usage', None)

        if not usage:
            continue  # skip if no usage reported

        in_tok = getattr(usage, 'input_tokens', 0) or 0
        out_tok = getattr(usage, 'output_tokens', 0) or 0
        details = getattr(usage, 'input_tokens_details', None)
        cached_tok = getattr(details, 'cached_tokens', 0) if details else 0

        billable_in_tok = max(in_tok - cached_tok, 0)

        input_cost = (billable_in_tok / 1_000_000) * rates.input_usd
        cached_cost = (cached_tok / 1_000_000) * rates.cached_input_usd
        output_cost = (out_tok / 1_000_000) * rates.output_usd

        total_cost += input_cost + cached_cost + output_cost

    return round(total_cost, 6)
