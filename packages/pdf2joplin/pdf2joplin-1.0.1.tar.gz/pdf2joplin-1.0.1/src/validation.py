import click

import os
import re


def file_exists(ctx, param, value):
    if value != '' and not os.path.isfile(value):
        raise click.BadParameter(f"The file '{value}' does not exist.")

    return value


def openai_api_key(ctx, param, value):
    openai_key_regex = r'^(sk-|sk-proj-)[a-zA-Z0-9_-]+$'

    if value != '' and not re.match(openai_key_regex, value):
        raise click.BadParameter(f"The key '{value}' is not a valid openai API key.")

    return value
