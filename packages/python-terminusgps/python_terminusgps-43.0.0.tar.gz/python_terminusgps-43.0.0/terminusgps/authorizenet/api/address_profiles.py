from authorizenet import apicontractsv1, apicontrollers
from lxml.objectify import ObjectifiedElement

from terminusgps.authorizenet.auth import get_merchant_auth
from terminusgps.authorizenet.controllers import execute_controller

__all__ = [
    "create_customer_shipping_address",
    "get_customer_shipping_address",
    "update_customer_shipping_address",
    "delete_customer_shipping_address",
]


def create_customer_shipping_address(
    customer_profile_id: int,
    address: apicontractsv1.customerAddressType,
    default: bool = True,
) -> ObjectifiedElement | None:
    """
    `createCustomerShippingAddressRequest <https://developer.authorize.net/api/reference/index.html#customer-profiles-create-customer-shipping-address>`_.

    :param customer_profile_id: An Authorizenet customer profile id.
    :type customer_profile_id: :py:obj:`int`
    :param elem: An Authorizenet customer address element.
    :type elem: :py:obj:`~authorizenet.apicontractsv1.customerAddressType`
    :param default: Whether or not to mark the new shipping address as default. Default is :py:obj:`True`.
    :type default: :py:obj:`bool`
    :returns: An Authorizenet createCustomerShippingAddress response.
    :rtype: :py:obj:`~lxml.objectify.ObjectifiedElement` | :py:obj:`None`

    """
    request = apicontractsv1.createCustomerShippingAddressRequest()
    request.merchantAuthentication = get_merchant_auth()
    request.customerProfileId = str(customer_profile_id)
    request.address = address
    request.defaultShippingAddress = str(default).lower()

    return execute_controller(
        apicontrollers.createCustomerShippingAddressController(request)
    )


def get_customer_shipping_address(
    customer_profile_id: int, address_profile_id: int
) -> ObjectifiedElement | None:
    """
    `getCustomerShippingAddressRequest <https://developer.authorize.net/api/reference/index.html#customer-profiles-get-customer-shipping-address>`_.

    :param customer_profile_id: An Authorizenet customer profile id.
    :type customer_profile_id: :py:obj:`int`
    :param address_profile_id: An Authorizenet customer address profile id.
    :type address_profile_id: :py:obj:`int`
    :returns: An Authorizenet getCustomerShippingAddress response.
    :rtype: :py:obj:`~lxml.objectify.ObjectifiedElement` | :py:obj:`None`

    """
    request = apicontractsv1.getCustomerShippingAddressRequest()
    request.merchantAuthentication = get_merchant_auth()
    request.customerProfileId = str(customer_profile_id)
    request.customerAddressId = str(address_profile_id)

    return execute_controller(
        apicontrollers.getCustomerShippingAddressController(request)
    )


def update_customer_shipping_address(
    customer_profile_id: int,
    address: apicontractsv1.customerAddressType,
    default: bool = False,
) -> ObjectifiedElement | None:
    """
    `updateCustomerShippingAddressRequest <https://developer.authorize.net/api/reference/index.html#customer-profiles-update-customer-shipping-address>`_.

    :param customer_profile_id: An Authorizenet customer profile id.
    :type customer_profile_id: :py:obj:`int`
    :param address: An Authorizenet customer address element.
    :type address: :py:obj:`~authorizenet.apicontractsv1.customerAddressType`
    :param default: Whether or not to mark the new shipping address as default. Default is :py:obj:`False`.
    :type default: :py:obj:`bool`
    :returns: An Authorizenet updateCustomerShippingAddress response.
    :rtype: :py:obj:`~lxml.objectify.ObjectifiedElement` | :py:obj:`None`

    """
    request = apicontractsv1.updateCustomerShippingAddressRequest()
    request.merchantAuthentication = get_merchant_auth()
    request.customerProfileId = str(customer_profile_id)
    request.address = address
    request.defaultShippingAddress = str(default).lower()

    return execute_controller(
        apicontrollers.updateCustomerShippingAddressController(request)
    )


def delete_customer_shipping_address(
    customer_profile_id: int, address_profile_id: int
) -> ObjectifiedElement | None:
    """
    `deleteCustomerShippingAddressRequest <https://developer.authorize.net/api/reference/index.html#customer-profiles-delete-customer-shipping-address>`_.

    :param customer_profile_id: An Authorizenet customer profile id.
    :type customer_profile_id: :py:obj:`int`
    :param address_profile_id: An Authorizenet customer address profile id.
    :type address_profile_id: :py:obj:`int`
    :returns: An Authorizenet deleteCustomerShippingAddressResponse element.
    :rtype: :py:obj:`~lxml.objectify.ObjectifiedElement` | :py:obj:`None`

    """
    request = apicontractsv1.deleteCustomerShippingAddressRequest()
    request.merchantAuthentication = get_merchant_auth()
    request.customerProfileId = str(customer_profile_id)
    request.customerAddressId = str(address_profile_id)

    return execute_controller(
        apicontrollers.deleteCustomerShippingAddressController(request)
    )
