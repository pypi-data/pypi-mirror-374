from typing import List
from ethereal.constants import API_PREFIX
from ethereal.models.rest import SubaccountDto, SubaccountBalanceDto


async def list_subaccounts(self, **kwargs) -> List[SubaccountDto]:
    """Lists subaccounts for a given sender (address).

    Args:
        sender (str): Wallet address to query subaccounts for. Required.

    Other Parameters:
        order (str, optional): Sort order, 'asc' or 'desc'. Optional.
        limit (float, optional): Maximum number of results to return. Optional.
        cursor (str, optional): Pagination cursor for fetching the next page. Optional.
        order_by (str, optional): Field to order by (e.g., 'createdAt'). Optional.
        **kwargs: Additional request parameters accepted by the API. Optional.

    Returns:
        List[SubaccountDto]: Subaccount records for the sender.
    """
    res = await self.get_validated(
        url_path=f"{API_PREFIX}/subaccount/",
        request_model=self._models.V1SubaccountGetParametersQuery,
        response_model=self._models.PageOfSubaccountDtos,
        **kwargs,
    )
    data = [
        self._models.SubaccountDto(**model.model_dump(by_alias=True))
        for model in res.data
    ]
    return data


async def get_subaccount(self, id: str, **kwargs) -> SubaccountDto:
    """Gets a specific subaccount by ID.

    Args:
        id (str): UUID of the subaccount. Required.

    Other Parameters:
        **kwargs: Additional request parameters accepted by the API. Optional.

    Returns:
        SubaccountDto: Subaccount details.
    """
    endpoint = f"{API_PREFIX}/subaccount/{id}"
    res = await self.get(endpoint, **kwargs)
    return self._models.SubaccountDto(**res)


async def get_subaccount_balances(self, **kwargs) -> List[SubaccountBalanceDto]:
    """Gets token balances for a subaccount.

    Args:
        subaccount_id (str): UUID of the subaccount. Required.

    Other Parameters:
        **kwargs: Additional request parameters accepted by the API. Optional.

    Returns:
        List[SubaccountBalanceDto]: Balances for the subaccount.
    """
    res = await self.get_validated(
        url_path=f"{API_PREFIX}/subaccount/balance",
        request_model=self._models.V1SubaccountBalanceGetParametersQuery,
        response_model=self._models.PageOfSubaccountBalanceDtos,
        **kwargs,
    )
    data = [
        self._models.SubaccountBalanceDto(**model.model_dump(by_alias=True))
        for model in res.data
    ]
    return data
