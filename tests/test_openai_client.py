import json
import pytest

from unittest.mock import AsyncMock

import scraper.openai_client as oc


@pytest.mark.asyncio
async def test_build_prompt():
    assert oc.build_prompt('hello') == 'hello'


@pytest.mark.asyncio
async def test_fetch_shopping_items_parses_json(monkeypatch):
    raw = '[{"title":"foo","price":1.23,"urls":["u"]}]'
    dummy = type('R', (), {'output_text': raw})
    monkeypatch.setattr(oc._client.responses, 'create', AsyncMock(return_value=dummy))
    items = await oc.fetch_shopping_items('p')
    assert isinstance(items, list)
    assert items[0]['title'] == 'foo'


@pytest.mark.asyncio
async def test_strip_json_fence(monkeypatch):
    inner = '[{"title":"bar","price":null,"urls":[]}]'
    fenced = f'```json\n{inner}\n```'
    dummy = type('R', (), {'output_text': fenced})
    monkeypatch.setattr(oc._client.responses, 'create', AsyncMock(return_value=dummy))
    items = await oc.fetch_shopping_items('p')
    assert items and items[0]['title'] == 'bar'


@pytest.mark.asyncio
async def test_fetch_shopping_items_invalid_json(monkeypatch):
    dummy = type('R', (), {'output_text': 'not json'})
    monkeypatch.setattr(oc._client.responses, 'create', AsyncMock(return_value=dummy))
    with pytest.raises(RuntimeError):
        await oc.fetch_shopping_items('p')