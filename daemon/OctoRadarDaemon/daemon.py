from datetime import datetime, timedelta
from logging import getLogger
import time

from .dao.repository_dao import RepositoryDao
from .dao.organizations_dao import OrganizationsDao
from .services.github import GitException, GithubClient

log = getLogger(__name__)


class DaemonException(Exception):
    """
    Typed exception raised when an error ocurrs while running the daemon.

    :param str msg: the error message.
    """
    def __init__(self, msg):
        self.msg = msg
        super().__init__(
            'Exception while running the daemon: {}'.format(msg)
        )


class Daemon:

    def __init__(self, config):
        self.config = config
        self.github_client = GithubClient(
            self.config.github.token,
            self.config.github.api_url
        )

        self.organization_dao = OrganizationsDao(
            self.config.databases.mongodb.host,
            self.config.databases.mongodb.port,
            self.config.databases.mongodb.database
        )

        self.repo_dao = RepositoryDao(
            self.config.databases.mongodb.host,
            self.config.databases.mongodb.port,
            self.config.databases.mongodb.database
        )

    def run(self):
        """
        Initiates the daemon to periodically fetch data from GitHub.

        This method starts a loop that continuously calls the
        `_get_github_data` method at a frequency determined by the
        `config.daemon.interval` setting. The interval is specified in minutes.
        In case the daemon returns error responses 10 times in a row the
        daemon will exit.

        The `_get_github_data` method is expected to handle all data fetching
        and processing tasks. This method simply schedules those tasks at the
        specified interval.
        """
        errors_count = 0
        while errors_count < 10:
            log.info('Executing get github data')
            start = time.time()
            try:
                self._get_github_data()
                errors_count = 0
            except GitException as e:
                log.error(e)
                errors_count += 1
            except DaemonException as e:
                log.error(e)
                errors_count += 1
            duration = round((time.time() - start)/60)
            log.info('Execution time: {} minutes'.format(duration))
            minutes_left = self.config.daemon.interval - duration
            if minutes_left < 0:
                minutes_left = 0

            log.info('Sleeping for {} minutes'.format(minutes_left))
            time.sleep(minutes_left*60)

        log.critical('Reached the maximum number of errors. Exiting.')

    def _update_github_organizations(self, github_organizations, orgs_in_db):
        """
        This method will update the organizations in the database. Will
        insert new organizations and delete organizations that are no longer
        active.

        :param list[dict] github_organizations: A list of organizations
         retrieved from GitHub.
        :param list[dict] orgs_in_db: A list of organizations
         retrieved from the database.

        :raises DaemonException: if an error occurs while inserting
         organizations.
        """
        github_orgs_names = {org['login'] for org in github_organizations}
        db_orgs_names = {org['name'] for org in orgs_in_db}
        new_orgs = github_orgs_names - db_orgs_names
        log.info(
            'Found {} new orgs, inserting to the db...'.format(len(new_orgs))
        )
        for org in github_organizations:
            if org['login'] in new_orgs:
                inserted_id = self.organization_dao.insert_one(
                    org['login'], ""
                )
                if not inserted_id:
                    raise DaemonException(
                        'Error while inserting org {} into the db'
                        .format(org['login'])
                    )
        log.info('Done\n')

        deleted_orgs = self.organization_dao.find_organizations_not_in_list(
            list(github_orgs_names)
        )
        deleted_orgs_names = [org['name'] for org in deleted_orgs]
        log.info(
            'Found {} deleted orgs, deleting from the db...'
            .format(len(deleted_orgs))
        )
        count = self.organization_dao.delete_organizations(deleted_orgs_names)
        if count != len(deleted_orgs_names):
            log.error(
                'Error while deleting orgs from the database, deleted {} orgs'
                .format(count)
            )
        log.info('Done\n')

    def _check_repository_size(self, current_size_object, new_size):
        """
        Check the last item in current_size_object, get the time the size was
        registered, then compare with the current time and check if the
        difference is bigger than the configured time interval. If it is, then
        insert a new size item with current timestamp.

        :param list[dict] current_size_object: A list of dictionaries
         containing the size entries of the repository.
        :param dict new_size: A dictionary containing the current size entry
         of the repository.

        :return: A list of dictionaries containing the size entries of the
         repository.
        :rtype: list[dict]
        """
        if not current_size_object:
            return [new_size]

        # Sort the list of dictionaries by 'timestamp' field
        current_size_object.sort(key=lambda x: x['timestamp'])

        last_item = current_size_object[-1]
        last_registered_time = last_item['timestamp']

        time_difference = new_size['timestamp'] - last_registered_time
        days_to_wait = timedelta(
            days=self.config.daemon.repository_size_info_days_interval)

        if time_difference > days_to_wait:
            current_size_object.append(new_size)

        return current_size_object

    def _get_repo_info(self, repo, org_name):
        """
        Fetch repository info from GitHub.

        :param str repo: The repository name.
        :param str org_name: The organization name.

        :return: A dictionary containing the repository info.
        :rtype: dict
        """
        repo_languages = self.github_client.get_repository_languages(
            org_name, repo['name'])
        repo_contributors = self.github_client.get_repository_contributors(
            org_name, repo['name'])
        contributors_info = None
        if repo_contributors:
            contributors_info = []
            for contributor in repo_contributors:
                contributors_info.append(
                    {
                        'name': contributor['login'],
                        'contributions': contributor['contributions']
                    }
                )

        result = {
            'name': repo['name'],
            'organization': org_name,
            'created_at': repo['created_at'],
            'latest_commit_at': repo['pushed_at'],
            'archived': repo['archived'],
            'disabled': repo['disabled'],
            'open_issues': repo['open_issues_count'],
            'has_issues': repo['has_issues'],
            'url': repo['html_url'],
            'default_branch': repo['default_branch'],
            'main_language': repo['language'],
            'languages': repo_languages,
            'contributors': contributors_info,
            'last_update_in_db': datetime.now(),
            'size': [{'size': repo['size'], 'timestamp': datetime.now()}],
        }
        return result

    def _update_repository_info_in_db(self, repo_document):
        """
        Update repository info in the database.

        :param dict repo_document: A dictionary containing the repository
         info.
        """
        current_doc_lst = self.repo_dao.find_all(
            repo_document['name'], repo_document['organization']
        )
        if current_doc_lst:
            log.info('Document already in db, updating...')
            current_doc = current_doc_lst[0]
            repo_document['size'] = self._check_repository_size(
                current_doc.get('size'), repo_document['size'][0]
            )
            modified_count = self.repo_dao.update_one(
                repo_document['name'],
                repo_document['organization'],
                repo_document
            )
            if not modified_count:
                raise DaemonException(
                    'Failed to update doc in the db for repo {} and org {}'
                    .format(
                        repo_document['name'], repo_document['organization']
                    )
                )
            log.info('Document updated')
            return

        log.info('Document not found, inserting new document...')
        inserted_id = self.repo_dao.insert_one(repo_document)
        if not inserted_id:
            raise DaemonException(
                'Failed to insert doc into the db for repo {} and org {}'
                .format(
                    repo_document['name'], repo_document['organization']
                )
            )
        log.info('Document inserted')

    def _get_github_data(self):
        """
        Fetches data from GitHub and stores it in the database.

        This method is responsible for fetching data from GitHub and storing
        it in the database. It is expected to handle all data fetching and
        processing tasks.
        """
        log.info('Daemon start!')

        log.info('Checking organizations...')
        organizations_in_db = self.organization_dao.find_all()
        organizations_found = {org['name'] for org in organizations_in_db}
        fetch_orgs = self.config.daemon.fetch_organizations
        if fetch_orgs or len(organizations_in_db) == 0:
            log.info('Fetching organizations from github...')
            organizations = self.github_client.get_organizations()
            self._update_github_organizations(
                organizations, organizations_in_db
            )
            organizations_found = {org['login'] for org in organizations}

        log.info('Found {} organizations'.format(len(organizations_found)))

        for index, org_name in enumerate(organizations_found, 1):
            log.info(
                'Total Completed: {}%\n'
                .format(round((index/len(organizations_found)*100)))
            )
            try:
                repos = self.github_client.get_organization_repositories(
                    org_name
                )
            except GitException as e:
                log.error(
                    'Error while retrieving repo for org {}: {}'
                    .format(org_name, e)
                )
                continue
            log.info(
                'Found {} repositories for organization {}'
                .format(len(repos), org_name)
            )

            for repo_index, repo in enumerate(repos, 1):
                log.info(
                    'Fetching info for repository: {}... Org Completed: {}%'
                    .format(repo['name'], round((repo_index/len(repos)*100)))
                )
                repo_info = self._get_repo_info(repo, org_name)
                log.info('Updating repository info in the database...')
                self._update_repository_info_in_db(repo_info)
                log.info('Done')

            log.info('Done\n')
