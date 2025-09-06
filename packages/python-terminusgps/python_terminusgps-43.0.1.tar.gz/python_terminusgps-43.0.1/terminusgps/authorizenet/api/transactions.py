import datetime

from authorizenet import apicontractsv1, apicontrollers
from lxml.objectify import ObjectifiedElement

from terminusgps.authorizenet.auth import get_merchant_auth
from terminusgps.authorizenet.controllers import execute_controller

__all__ = []


def get_settled_batch_list(
    start: datetime.datetime,
    end: datetime.datetime,
    include_statistics: bool = False,
) -> ObjectifiedElement | None:
    """
    `getSettledBatchListRequest <https://developer.authorize.net/api/reference/index.html#transaction-reporting-get-settled-batch-list>`_.

    :param start: First settlement date.
    :type start: :py:obj:`~datetime.datetime`
    :param end: Last settlement date.
    :type end: :py:obj:`~datetime.datetime`
    :returns: An Authorizenet getSettledBatchListResponse element.
    :rtype: :py:obj:`~lxml.objectify.ObjectifiedElement` | :py:obj:`None`

    """
    request = apicontractsv1.getSettledBatchListRequest()
    request.merchantAuthentication = get_merchant_auth()
    request.includeStatistics = str(include_statistics).lower()
    request.firstSettlementDate = start
    request.lastSettlementDate = end

    return execute_controller(
        apicontrollers.getSettledBatchListController(request)
    )


def get_transaction_list(
    batch_id: int,
    ordering: str = "submitTimeUTC",
    descending: bool = False,
    limit: int = 1000,
    offset: int = 0,
) -> ObjectifiedElement | None:
    """
    `getTransactionListRequest <https://developer.authorize.net/api/reference/index.html#transaction-reporting-get-transaction-list>`_.

    :param batch_id: An Authorizenet transaction batch id.
    :type batch_id :py:obj:`int`
    :param ordering: An Authorizenet transaction list ordering string. Default is :py:obj:`"submitTimeUTC"`.
    :type ordering: :py:obj:`str`
    :param descending: Whether to sort the transaction list in descending order. Default is :py:obj:`False` (ascending order).
    :type descending: :py:obj:`bool`
    :param limit: Total number of transactions to return in the list.
    :type limit: :py:obj:`int`
    :param offset: Page number to return results from.
    :type offset: :py:obj:`int`
    :returns: An Authorizenet getTransactionListResponse element.
    :rtype: :py:obj:`~lxml.objectify.ObjectifiedElement` | :py:obj:`None`

    """
    sorting = apicontractsv1.TransactionListSorting()
    sorting.orderBy = ordering
    sorting.orderDescending = str(descending).lower()

    paging = apicontractsv1.Paging()
    paging.limit = str(limit)
    paging.offset = str(offset)

    request = apicontractsv1.getTransactionListRequest()
    request.merchantAuthentication = get_merchant_auth()
    request.batchId = str(batch_id)
    request.sorting = sorting
    request.paging = paging

    return execute_controller(
        apicontrollers.getTransactionListController(request)
    )
