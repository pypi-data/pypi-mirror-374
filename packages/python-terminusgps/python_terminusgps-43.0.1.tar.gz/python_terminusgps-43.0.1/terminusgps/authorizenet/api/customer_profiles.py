from authorizenet import apicontractsv1, apicontrollers
from lxml.objectify import ObjectifiedElement

from terminusgps.authorizenet.auth import get_merchant_auth
from terminusgps.authorizenet.controllers import execute_controller

__all__ = [
    "create_customer_profile",
    "get_customer_profile",
    "get_customer_profile_ids",
    "update_customer_profile",
    "delete_customer_profile",
]


def create_customer_profile(
    merchant_id: str, email: str, description: str = ""
) -> ObjectifiedElement | None:
    """
    `createCustomerProfileRequest <https://developer.authorize.net/api/reference/index.html#customer-profiles-create-customer-profile>`_.

    :param merchant_id: A merchant designated customer id.
    :type merchant_id: :py:obj:`str`
    :param email: A customer email address.
    :type email: :py:obj:`str`
    :param description: An optional customer description.
    :type description: :py:obj:`str`
    :returns: An Authorizenet createCustomerProfile response.
    :rtype: :py:obj:`~lxml.objectify.ObjectifiedElement` | :py:obj:`None`

    """
    request = apicontractsv1.createCustomerProfileRequest()
    request.merchantAuthentication = get_merchant_auth()
    request.profile = apicontractsv1.customerProfileType()
    request.profile.merchantCustomerId = merchant_id
    request.profile.description = description
    request.profile.email = email

    return execute_controller(
        apicontrollers.createCustomerProfileController(request)
    )


def get_customer_profile(
    customer_profile_id: int, include_issuer_info: bool = False
) -> ObjectifiedElement | None:
    """
    `getCustomerProfileRequest <https://developer.authorize.net/api/reference/index.html#customer-profiles-get-customer-profile>`_.

    :param customer_profile_id: An Authorizenet customer profile id.
    :type customer_profile_id: :py:obj:`int`
    :param include_issuer_info: Whether or not to include issuer info in the response. Default is :py:obj:`False`.
    :type include_issuer_info: :py:obj:`bool`
    :returns: An Authorizenet getCustomerProfile response.
    :rtype: :py:obj:`~lxml.objectify.ObjectifiedElement` | :py:obj:`None`

    """
    request = apicontractsv1.getCustomerProfileRequest()
    request.merchantAuthentication = get_merchant_auth()
    request.customerProfileId = str(customer_profile_id)
    request.includeIssuerInfo = str(include_issuer_info).lower()

    return execute_controller(
        apicontrollers.getCustomerProfileController(request)
    )


def get_customer_profile_ids() -> ObjectifiedElement | None:
    """
    `getCustomerProfileIdsRequest <https://developer.authorize.net/api/reference/index.html#customer-profiles-get-customer-profile-ids>`_.

    :returns: An Authorizenet getCustomerProfileIds response.
    :rtype: :py:obj:`~lxml.objectify.ObjectifiedElement` | :py:obj:`None`

    """
    request = apicontractsv1.getCustomerProfileIdsRequest()
    request.merchantAuthentication = get_merchant_auth()

    return execute_controller(
        apicontrollers.getCustomerProfileIdsController(request)
    )


def update_customer_profile(
    profile: apicontractsv1.customerProfileExType,
) -> ObjectifiedElement | None:
    """
    `updateCustomerProfileRequest <https://developer.authorize.net/api/reference/index.html#customer-profiles-update-customer-profile>`_.

    :param profile: An Authorizenet customer profile ex element.
    :type profile: :py:obj:`~authorizenet.apicontractsv1.customerProfileExType`
    :returns: An Authorizenet updateCustomerProfile response.
    :rtype: :py:obj:`~lxml.objectify.ObjectifiedElement` | :py:obj:`None`

    """
    request = apicontractsv1.updateCustomerProfileRequest()
    request.merchantAuthentication = get_merchant_auth()
    request.profile = profile

    return execute_controller(
        apicontrollers.updateCustomerProfileController(request)
    )


def delete_customer_profile(
    customer_profile_id: int,
) -> ObjectifiedElement | None:
    """
    `deleteCustomerProfileRequest <https://developer.authorize.net/api/reference/index.html#customer-profiles-delete-customer-profile>`_.

    :param customer_profile_id: An Authorizenet customer profile id.
    :type customer_profile_id: :py:obj:`int`
    :returns: An Authorizenet deleteCustomerProfile response.
    :rtype: :py:obj:`~lxml.objectify.ObjectifiedElement` | :py:obj:`None`

    """
    request = apicontractsv1.deleteCustomerProfileRequest()
    request.merchantAuthentication = get_merchant_auth()
    request.customerProfileId = str(customer_profile_id)

    return execute_controller(
        apicontrollers.deleteCustomerProfileController(request)
    )
