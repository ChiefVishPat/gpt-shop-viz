from datetime import datetime, timedelta, timezone

import pytest

from app import crud, schemas


@pytest.mark.asyncio
async def test_crud_product_and_snapshot(db_session, override_db):
    # No products initially
    products = await crud.get_products(db_session)
    assert products == []

    # Create a product
    prod_in = schemas.ProductCreate(name='Test', prompt='test-prompt')
    prod = await crud.create_product(db_session, prod_in)
    assert prod.id is not None
    assert prod.name == 'Test'
    assert prod.prompt == 'test-prompt'
    assert prod.snapshots == []

    # get_products should now return one
    all_prods = await crud.get_products(db_session)
    assert len(all_prods) == 1

    # get_product by ID
    fetched = await crud.get_product(db_session, prod.id)
    assert fetched.id == prod.id

    # get_or_create_product returns existing when prompt matches
    same = await crud.get_or_create_product(db_session, name='X', prompt='test-prompt')
    assert same.id == prod.id

    # Create two snapshots: one recent, one older
    snap1 = schemas.SnapshotCreate(
        product_id=prod.id,
        title='snap1',
        price=1.0,
        urls=['u1'],
    )
    res1 = await crud.create_snapshot(db_session, snap1)
    assert res1.id is not None

    old_time = datetime.now(timezone.utc) - timedelta(days=1)
    snap2 = schemas.SnapshotCreate(
        product_id=prod.id,
        title='snap2',
        price=0.5,
        urls=['u2'],
        captured_at=old_time,
    )
    res2 = await crud.create_snapshot(db_session, snap2)

    # Latest snapshots (most recent timestamp)
    latest = await crud.get_latest_snapshots(db_session, prod.id)
    assert len(latest) == 1 and latest[0].id == res1.id

    # History for 2 days should include both
    history = await crud.get_snapshot_history(db_session, prod.id, days=2)
    assert {s.id for s in history} == {res1.id, res2.id}

    # Best price (lowest) should pick the older, lower-priced snapshot
    best = await crud.get_lowest_price_period(db_session, prod.id)
    assert best.id == res2.id
