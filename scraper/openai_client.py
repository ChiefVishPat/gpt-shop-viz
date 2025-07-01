"""
OpenAI client for fetching shopping items.

Builds prompts and invokes ChatCompletion, then parses the JSON output
into a list of product entries with title, price, and URLs.
"""

import json
import os
import re
from typing import Any, Dict, List, cast

from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()

_client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))

_SYSTEM_PROMPT = """
You are a 'ChatGPT Shopping' shopping assistant.  Given a user request, return *only* valid JSON (no markdown fences, no extra text)—
an array of objects, each with these keys:
  • title: string, the product name
  • price: number or null, price in USD
  • urls: array of strings, **all** direct, working links to that product’s pages (manufacturer site, major retailers, marketplaces, etc.).  
    Do not artificially limit the list; include every relevant URL you can find.
  Do not include any other fields or commentary.
    """


def build_prompt(user_input: str) -> str:
    """
    Right now it’s a no-op, but you can evolve it without touching fetch_shopping_items

    Accept whatever the user types (e.g. “Show me headsets under $200…”),
    and pass it straight through as the ChatGPT “user” message.

    Currently returns the user’s input unmodified.
    """
    return user_input


async def fetch_shopping_items(raw_prompt: str) -> List[Dict[str, Any]]:
    """
    Sends the user’s prompt to OpenAI’s ChatCompletion endpoint,
    then parses and returns the resulting JSON array.

    :param raw_prompt: The shopping prompt entered by the user.
    :return: A list of dictionaries, each with keys "title", "price", and "urls".
    :raises RuntimeError: If the API response is not valid JSON.
    """
    user_prompt = build_prompt(raw_prompt)
    resp = await _client.responses.create(
        model='gpt-4.1-nano',
        input=[
            {'role': 'system', 'content': _SYSTEM_PROMPT},
            {'role': 'user', 'content': user_prompt},
        ],
    )

    # 1) grab the assistant’s text block (ensure structure exists)
    try:
        raw: str = resp.output_text
    except (IndexError, AttributeError) as e:
        raise RuntimeError(f'Invalid response structure from OpenAI: {resp}') from e

    # 2) strip any ```json … ``` fence, pulling out the [...] block
    m = re.search(r'```json\s*([\s\S]+?)\s*```', raw, re.IGNORECASE)
    json_str = m.group(1) if m else raw

    # 3) parse it
    try:
        parsed = json.loads(json_str)
    except json.JSONDecodeError as e:
        raise RuntimeError(f'Failed to parse JSON from model output:\n{raw}') from e

    if not isinstance(parsed, list):
        raise RuntimeError(f'Expected a JSON list but got: {type(parsed).__name__}')

    return cast(List[Dict[str, Any]], parsed)


if __name__ == '__main__':
    import asyncio
    import pprint

    prompt = input('Enter a shopping prompt: ').strip()
    try:
        items = asyncio.run(fetch_shopping_items(prompt))
    except Exception as e:
        print('Error calling OpenAI:', e)
    else:
        print('\n✅ Parsed JSON:')
        pprint.pp(items)
