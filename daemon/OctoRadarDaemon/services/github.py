from logging import getLogger

import requests


log = getLogger(__name__)


class GitException(Exception):
    """
    Typed exception raised when a request to github returns a status code
    different than 200.

    :param int status_code: status code returned from the github endpoint.
    :param str url: the url that was called.
    """

    def __init__(self, status_code, url):
        self.status_code = status_code
        super().__init__(
            'Request to Github returned invalid status code: {}, for url: {}'
            .format(status_code, url)
        )


class GithubClient:
    """
    Class for interacting with the GitHub API.

    :para str token: the GitHub access token.
    :param str api_url: the GitHub API url.
    """

    def __init__(self, token, api_url):
        self.api_url = api_url
        self.token = token

    def _authenticated_get_request(self, api):
        """
        Performs an authenticated GET request to the specified github url.

        :param str url: the url to call

        :return: the response data parsed to json (if API returns 200 http
         status code)
        :rtype: dict

        :raises GitException: if the API returns a status code different than
         200.
        """
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }

        final_url = self.api_url + api
        response = requests.get(final_url, headers=headers)

        if response.status_code == 204:
            log.warning('No content returned from url: {}'.format(final_url))
            return None

        if response.status_code != 200:
            raise GitException(response.status_code, final_url)

        data = response.json()
        return data

    def get_organizations(self):
        """
        Retrieves all organizations to which the user has access.

        :return: the response data parsed to json (if API returns 200 http
         status code)
        :rtype: dict

        :raises GitException: if the API returns a status code different than
         200.
        """
        return self._authenticated_get_request('/user/orgs')

    def get_organization_repositories(self, org_name):
        """
        Retrieves all repositories for the specified organization.

        :param str org_name: the name of the organization.

        :return: the response data parsed to json (if API returns 200 http
         status code)
        :rtype: dict

        :raises GitException: if the API returns a status code different than
         200.
        """
        return self._authenticated_get_request(f"/orgs/{org_name}/repos")

    def get_repository_contributors(self, org_name, repo_name):
        """
        Retrieves all contributors for the specified repository.

        :param str org_name: the name of the organization.
        :param str repo_name: the name of the repository.

        :return: the response data parsed to json (if API returns 200 http
         status code)
        :rtype: dict

        :raises GitException: if the API returns a status code different than
         200.
        """
        try:
            return self._authenticated_get_request(
                f"/repos/{org_name}/{repo_name}/contributors"
            )
        except GitException as e:
            log.error(
                'Error while retrieving contributors for repository {}/{}: {}'
                .format(org_name, repo_name, e)
            )
            return None

    def get_repository_languages(self, org_name, repo_name):
        """
        Retrieves all languages for the specified repository.

        :param str org_name: the name of the organization.
        :param str repo_name: the name of the repository.

        :return: the response data parsed to json (if API returns 200 http
         status code) or None if there is an error.
        :rtype: dict or None
        """
        try:
            return self._authenticated_get_request(
                f"/repos/{org_name}/{repo_name}/languages"
            )
        except GitException as e:
            log.error(
                'Error while retrieving languages for repository {}/{}: {}'
                .format(org_name, repo_name, e)
            )
            return None


__all__ = [
    'GitException',
    'GithubClient',
]
