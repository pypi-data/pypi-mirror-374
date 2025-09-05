"""Pure async tests for REST info endpoints that require an account."""

import pytest
from typing import List
from pydantic import BaseModel


@pytest.mark.asyncio
async def test_rest_info_subaccount_balances(async_rc, network):
    sid = (await async_rc.subaccounts())[0].id
    balances = await async_rc.get_subaccount_balances(subaccount_id=sid)
    assert isinstance(balances, List)
    assert all(isinstance(sb, BaseModel) for sb in balances)


@pytest.mark.asyncio
async def test_rest_info_orders(async_rc, network):
    sid = (await async_rc.subaccounts())[0].id
    orders = await async_rc.list_orders(subaccount_id=sid)
    assert isinstance(orders, List)
    assert all(isinstance(o, BaseModel) for o in orders)


@pytest.mark.asyncio
async def test_rest_info_fills(async_rc, network):
    sid = (await async_rc.subaccounts())[0].id
    fills = await async_rc.list_fills(subaccount_id=sid)
    assert isinstance(fills, List)
    assert all(isinstance(f, BaseModel) for f in fills)


@pytest.mark.asyncio
async def test_rest_info_fills_paginated(async_rc, network):
    sid = (await async_rc.subaccounts())[0].id
    fills = await async_rc._get_pages(
        endpoint="order/fill",
        request_model=async_rc._models.V1OrderFillGetParametersQuery,
        response_model=async_rc._models.PageOfOrderFillDtos,
        subaccount_id=sid,
        limit=500,
        paginate=True,
    )
    assert isinstance(fills, List)
    assert all(isinstance(f, BaseModel) for f in fills)


@pytest.mark.asyncio
async def test_rest_info_trades(async_rc, network):
    products = await async_rc.list_products()
    params = {"product_id": products[0].id, "order": "desc", "limit": 100}
    trades = await async_rc.list_trades(**params)
    assert isinstance(trades, List)
    assert all(isinstance(t, BaseModel) for t in trades)


@pytest.mark.asyncio
async def test_rest_info_positions(async_rc, network):
    sid = (await async_rc.subaccounts())[0].id
    positions = await async_rc.list_positions(subaccount_id=sid)
    assert isinstance(positions, List)
    assert all(isinstance(p, BaseModel) for p in positions)