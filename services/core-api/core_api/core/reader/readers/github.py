import logging
from pathlib import Path

import httpx
import base64
import yaml

from core_api.core.models import Application
from core_api.core.reader.models import CatCodeRepoEntry

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)  # Set logging level as per your requirement

class GithubReader:

    def __init__(self, token, username):
        self.token = token
        self.username = username
        self.tracked_file = 'catcode.yaml'

    def search_files(self):
        headers = {"Authorization": f"Bearer {self.token}"}
        api_url = "https://api.github.com/search/code"

        # GitHub API search query for the specified file
        query = f"filename:{self.tracked_file} user:{self.username}"
        params = {"q": query, "per_page": 9999}  # Adjust per_page as needed

        # Send HTTP GET request to GitHub API
        response = httpx.get(api_url, headers=headers, params=params)
        if response.status_code == 200:
            # Extract file paths from the response
            data = response.json()
            file_paths = [
                CatCodeRepoEntry(
                    repo=item['repository']['name'],
                    repo_path=item['path'],
                    sha=item['sha'],
                    user=item['repository']['owner']['login'],
                    url=item['repository']['url'],
                ) for item in data['items']]
            return file_paths
        else:
            logger.error("Error occurred while fetching data from GitHub API.")
            return None


    def files(self):
        return self.search_files()
    def request_header(self):
        return {"Authorization": f"Bearer {self.token}"}

    def fetch_file_content(self, repo_full_name, path, user):
        headers = {"Authorization": f"Bearer {self.token}"}
        api_url = f"https://api.github.com/repos/{user}/{repo_full_name}/contents/{path}"

        with httpx.Client() as client:
            response = client.get(api_url, headers=headers)

        if response.status_code == 200:
            content_data = response.json()
            if 'content' in content_data:
                # Decode the base64-encoded content
                content = base64.b64decode(content_data['content']).decode('utf-8')
                return content
            else:
                logger.error(f"Error: 'content' not found in API response")
                return None
        else:
            logger.error(f"Error: {response.status_code}")
            return None

    def get_file_content(self, repo: CatCodeRepoEntry):

        logger.info(f"Fetching content of catcode.yaml in repository: {repo.repo} at path {repo.repo_path}.")

        # Fetch the content of catcode.yaml in the repository
        try:
            catcode_yaml_content = self.fetch_file_content(repo.repo, repo.repo_path, repo.user)
        except Exception as e:
            logger.exception(f'Failed to read config from repo {repo.repo} at path {repo.repo_path}.\n')
            raise e
        if catcode_yaml_content is None:
            logger.error(f'Failed to find content for repository {repo.repo} at path {repo.repo_path}.')
        c = yaml.safe_load(catcode_yaml_content)

        entry = Application(**c)
        entry.metadata.annotations['catcode.io/github-url'] = repo.url
        entry.metadata.annotations['catcode.io/repo-path'] = Path(repo.repo_path).parent
        return entry


if __name__ == '__main__':
    # Replace with your GitHub username, token, and the desired file name
    github_username = "MatiWall"
    github_token = ""
    catcode_yaml_filename = ""
