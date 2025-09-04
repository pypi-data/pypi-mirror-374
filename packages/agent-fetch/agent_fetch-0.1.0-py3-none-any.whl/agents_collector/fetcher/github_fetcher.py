"""
GitHub file fetcher for agent-fetch.

Handles fetching files from GitHub repositories using their raw file endpoints
with support for different branches and robust error handling.
"""

import pathlib
import urllib.parse
from typing import Dict, List, Optional, Tuple
import requests


class GitHubFetcher:
    """Handles fetching files from GitHub repositories."""

    def __init__(self, timeout: int = 30, user_agent: str = "Agents-Collector-CLI/0.1.0"):
        """Initialize the GitHub fetcher.

        Args:
            timeout: Request timeout in seconds.
            user_agent: User-Agent string for HTTP requests.
        """
        self.timeout = timeout
        self.user_agent = user_agent
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": user_agent,
        })

    @staticmethod
    def parse_github_url(url: str) -> Tuple[str, str, str]:
        """Parse a GitHub repository URL to extract owner, repo, and branch.

        Args:
            url: GitHub repository URL (e.g., https://github.com/owner/repo)

        Returns:
            Tuple of (owner, repo, branch)

        Raises:
            ValueError: If the URL format is invalid.
        """
        try:
            parsed = urllib.parse.urlparse(url)
            if parsed.hostname != "github.com":
                raise ValueError("URL must be a GitHub repository URL")

            path_parts = parsed.path.strip("/").split("/")

            if len(path_parts) < 2:
                raise ValueError("Invalid GitHub repository URL format")

            owner = path_parts[0]
            repo = path_parts[1]

            # Default to main branch if not specified
            branch = "main"

            return owner, repo, branch

        except Exception as e:
            raise ValueError(f"Failed to parse GitHub URL '{url}': {e}")

    def build_raw_url(self, repo_url: str, file_path: str, branch: str = "main") -> str:
        """Build the GitHub raw file URL for a given repository file.

        Args:
            repo_url: GitHub repository URL.
            file_path: Path to the file within the repository.
            branch: Branch name (default: "main").

        Returns:
            Raw file URL.

        Raises:
            ValueError: If repository URL parsing fails.
        """
        owner, repo, _ = self.parse_github_url(repo_url)

        # Ensure file_path doesn't start with /
        file_path = file_path.lstrip("/")

        raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{file_path}"
        return raw_url

    def fetch_file(self, url: str, output_path: pathlib.Path, append: bool = False) -> bool:
        """Fetch a file from the given URL and save/append it to the output path.

        Args:
            url: File URL to fetch.
            output_path: Local path where to save/append the file.
            append: Whether to append to existing file instead of overwriting.

        Returns:
            True if successful, False otherwise.

        Raises:
            FileNotFoundError: If the remote file doesn't exist.
            OSError: If there are issues creating directories or writing the file.
            requests.RequestException: If there are network-related errors.
        """
        try:
            # Ensure the output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Make the HTTP request
            response = self.session.get(url, timeout=self.timeout, stream=True)

            if response.status_code == 404:
                raise FileNotFoundError(f"File not found at URL: {url}")
            elif response.status_code != 200:
                response.raise_for_status()

            # Write the file (append or overwrite)
            mode = "ab" if append else "wb"
            with open(output_path, mode) as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            return True

        except requests.Timeout:
            raise requests.RequestException(f"Timeout fetching file from {url}")
        except requests.ConnectionError:
            raise requests.RequestException(f"Connection error fetching file from {url}")
        except requests.HTTPError as e:
            raise requests.RequestException(f"HTTP error fetching file from {url}: {e}")
        except OSError as e:
            raise OSError(f"Failed to write file to {output_path}: {e}")

    def fetch_files_from_index(self,
                             repo_url: str,
                             file_entries: List[Dict[str, str]],
                             branch: str = "main",
                             overwrite: bool = True) -> Dict[str, bool]:
        """Fetch multiple files from a GitHub repository based on index entries.

        Args:
            repo_url: GitHub repository URL.
            file_entries: List of file entries with 'name', 'source', 'target' keys.
            branch: Branch name to fetch from.
            overwrite: Whether to overwrite existing files.

        Returns:
            Dictionary mapping file names to success status.
        """
        results = {}

        for entry in file_entries:
            name = entry.get("name", "Unknown")
            source = entry.get("source", "")
            target = entry.get("target", "")

            if not source or not target:
                results[name] = False
                continue

            # Build raw URL
            raw_url = self.build_raw_url(repo_url, source, branch)
            target_path = pathlib.Path(target)

            # Check if file exists - if it does, append instead of overwrite
            append_mode = target_path.exists()

            try:
                success = self.fetch_file(raw_url, target_path, append=append_mode)
                results[name] = success
            except (FileNotFoundError, OSError, requests.RequestException) as e:
                # Log the error (could add logging here)
                results[name] = False

        return results

    def validate_repo_url(self, url: str) -> bool:
        """Validate that a URL is a valid GitHub repository URL.

        Args:
            url: URL to validate.

        Returns:
            True if valid, False otherwise.
        """
        try:
            self.parse_github_url(url)
            return True
        except ValueError:
            return False

    def test_connection(self, repo_url: str, file_path: str = None, branch: str = "main") -> bool:
        """Test connection to a GitHub repository by trying to fetch a file.

        Args:
            repo_url: GitHub repository URL to test.
            file_path: Path to a file to test with (default: repository README).
            branch: Branch to test with.

        Returns:
            True if connection is successful, False otherwise.
        """
        if file_path is None:
            file_path = "README.md"  # Default test file

        try:
            raw_url = self.build_raw_url(repo_url, file_path, branch)
            response = self.session.head(raw_url, timeout=self.timeout)
            return response.status_code == 200
        except Exception:
            return False

    def get_available_branches(self, repo_url: str) -> List[str]:
        """Get list of available branches for a repository.

        Note: This is a simplified implementation. In a real-world scenario,
        you'd use the GitHub API to get branches. For now, we'll return common defaults.

        Args:
            repo_url: GitHub repository URL.

        Returns:
            List of branch names.
        """
        # For now, return common branch names
        # In a production implementation, this would use GitHub API
        return ["main", "master", "develop", "development"]
