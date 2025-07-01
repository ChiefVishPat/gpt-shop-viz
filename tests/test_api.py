import pytest

from app.main import fetch_shopping_items, app as fastapi_app


@pytest.mark.asyncio
async def test_health_endpoint(client):
    res = await client.get('/health')
    assert res.status_code == 200
    assert res.json() == {'status': 'ok'}


@pytest.mark.asyncio
async def test_product_lifecycle(client, monkeypatch):
    # Stub out OpenAI fetch to return predictable items
    fake_items = [
        {'title': 'A', 'price': 10, 'urls': ['u1']},
        {'title': 'B', 'price': 20, 'urls': ['u2']},
    ]
    async def fake_fetch(prompt):
        return fake_items

    # Monkeypatch imported fetch_shopping_items in the FastAPI module
    import app.main as main_mod
    monkeypatch.setattr(main_mod, 'fetch_shopping_items', fake_fetch)

    # Create a product
    payload = {'name': 'Prod', 'prompt': 'qry'}
    r1 = await client.post('/products', json=payload)
    assert r1.status_code == 200
    created = r1.json()
    pid = created['id']

    # List products
    r2 = await client.get('/products')
    assert r2.status_code == 200
    assert any(p['id'] == pid for p in r2.json())

    # Get product detail
    r3 = await client.get(f'/products/{pid}')
    assert r3.status_code == 200

    # Latest snapshots
    r4 = await client.get(f'/products/{pid}/latest')
    assert r4.status_code == 200
    latest = r4.json()
    assert isinstance(latest, list)

    # History (default 7 days)
    r5 = await client.get(f'/products/{pid}/history')
    assert r5.status_code == 200

    # Best price (should pick price=10)
    r6 = await client.get(f'/products/{pid}/best')
    assert r6.status_code == 200
    assert r6.json()['price'] == 10