"""
This module contains functions relating to user management.
"""

import logging
import os

import requests
from nacwrap._auth import Decorators
from nacwrap._helpers import _delete, _fetch_page
from nacwrap.data_model import NintexUser

logger = logging.getLogger(__name__)


@Decorators.refresh_token
def user_delete(id: str):
    """
    Delete a single Nintex User.

    :param id: Nintex User ID to delete.
    """

    url = os.environ["NINTEX_BASE_URL"] + f"/tenants/v1/users/{id}"

    try:
        response = _delete(
            url,
            headers={
                "Authorization": "Bearer " + os.environ["NTX_BEARER_TOKEN"],
                "Content-Type": "application/json",
            },
            params={},
        )
        response.raise_for_status()

    except requests.exceptions.HTTPError as e:
        logger.error(
            f"Error, user not found when deleting: {e.response.status_code} - {e.response.content}"
        )
        raise Exception(
            f"Error, user not found when deleting: {e.response.status_code} - {e.response.content}"
        )

    except requests.exceptions.RequestException as e:
        logger.error(f"Error, could not get instance data: {e}")
        raise Exception(f"Error, could not get instance data: {e}")

    if response.status_code != 204:
        logger.error(
            f"Error, invalid response code received when deleting user: {response.status_code} - {response.content}"
        )
        raise Exception(
            f"Error, invalid response code received when deleting user: {response.status_code} - {response.content}"
        )


@Decorators.refresh_token
def users_list(
    id: str | None = None,
    email: str | None = None,
    filter: str | None = None,
    role: str | None = None,
) -> list[dict]:
    """
    Get Nintex User Data.
    Returns: List of Dictionaries.

    :param id: User's ID filter
    :param email: User's email filter
    :param filter: User's name or email filter
    :param role: User's role filter
    """
    base_url = os.environ["NINTEX_BASE_URL"] + "/tenants/v1/users"
    params = {"id": id, "email": email, "filter": filter, "role": role}

    # Remove None values
    params = {k: v for k, v in params.items() if v is not None}

    results = []
    url = base_url
    first_request = True

    while url:
        # If this is subsequent requests, don't need to pass params
        # will be provided in the skip URL
        if first_request:
            first_request = False
        else:
            params = None

        try:
            response = _fetch_page(
                url,
                headers={
                    "Authorization": "Bearer " + os.environ["NTX_BEARER_TOKEN"],
                    "Content-Type": "application/json",
                },
                params=params,
            )
            response.raise_for_status()

        except requests.exceptions.HTTPError as e:
            logger.error(
                f"Error, could not get user data: {e.response.status_code} - {e.response.content}"
            )
            raise Exception(
                f"Error, could not get user data: {e.response.status_code} - {e.response.content}"
            )

        except requests.exceptions.RequestException as e:
            logger.error(f"Error, could not get user data: {e}")
            raise Exception(f"Error, could not get user data: {e}")

        data = response.json()
        results += data["users"]

        url = data.get("nextLink")

    return results


def users_list_pd(
    id: str | None = None,
    email: str | None = None,
    filter: str | None = None,
    role: str | None = None,
) -> list[NintexUser]:
    """
    Get Nintex User Data.
    Returns: List of NintexUser pydantic objects.

    :param id: User's ID filter
    :param email: User's email filter
    :param filter: User's name or email filter
    :param role: User's role filter
    """
    usr_dict = users_list(id=id, email=email, filter=filter, role=role)
    results: list[NintexUser] = []

    for user in usr_dict:
        results.append(NintexUser(**user))

    return results
