"""Pure sync tests for REST info endpoints that require an account."""

import pytest
from typing import List
from pydantic import BaseModel


def test_rest_info_subaccount_balances(rc, sid):
    balances = rc.get_subaccount_balances(subaccount_id=sid)
    assert isinstance(balances, List)
    assert all(isinstance(sb, BaseModel) for sb in balances)


def test_rest_info_orders(rc, sid):
    orders = rc.list_orders(subaccount_id=sid)
    assert isinstance(orders, List)
    assert all(isinstance(o, BaseModel) for o in orders)


def test_rest_info_fills(rc, sid):
    fills = rc.list_fills(subaccount_id=sid)
    assert isinstance(fills, List)
    assert all(isinstance(f, BaseModel) for f in fills)


def test_rest_info_fills_paginated(rc, sid):
    fills = rc._get_pages(
        endpoint="order/fill",
        request_model=rc._models.V1OrderFillGetParametersQuery,
        response_model=rc._models.PageOfOrderFillDtos,
        subaccount_id=sid,
        limit=500,
        paginate=True,
    )
    assert isinstance(fills, List)
    assert all(isinstance(f, BaseModel) for f in fills)


def test_rest_info_trades(rc, sid):
    products = rc.list_products()
    params = {"product_id": products[0].id, "order": "desc", "limit": 100}
    trades = rc.list_trades(**params)
    assert isinstance(trades, List)
    assert all(isinstance(t, BaseModel) for t in trades)


def test_rest_info_positions(rc, sid):
    positions = rc.list_positions(subaccount_id=sid)
    assert isinstance(positions, List)
    assert all(isinstance(p, BaseModel) for p in positions)