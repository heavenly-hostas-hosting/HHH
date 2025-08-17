import base64  # noqa: F401
import time
from typing import Any

import httpx
import jwt

from . import env


def get_app_token() -> str:
    """Generate a JWT token for the GitHub App."""
    now = int(time.time())
    payload = {
        "iat": now,
        "exp": now + (3 * 60),  # JWT valid for 3 minutes
        "iss": env.CLIENT_ID,  # GitHub App ID
    }

    return jwt.encode(payload, env.PRIVATE_KEY, algorithm="RS256")


async def get_app_installations(app_token: str) -> list[dict[str, Any]]:
    """Get all installations of the GitHub App."""
    headers = {
        "Authorization": f"Bearer {app_token}",
        "Accept": "application/vnd.github+json",
    }
    async with httpx.AsyncClient() as client:
        r = await client.get("https://api.github.com/app/installations", headers=headers)
        r.raise_for_status()
        return r.json()


async def get_app_installation_repositories(app_installation_token: str) -> dict[str, Any]:
    """Get all repositories a GitHub App installation has access to."""
    headers = {
        "Authorization": f"Bearer {app_installation_token}",
        "Accept": "application/vnd.github+json",
    }
    async with httpx.AsyncClient() as client:
        r = await client.get("https://api.github.com/installation/repositories", headers=headers)
        r.raise_for_status()
        return r.json()


async def get_app_installation_token(installation_id: int, app_token: str) -> str:
    """Get an installation token for the GitHub App.

    This token is used to perform actions on behalf of the installation.
    """
    headers = {
        "Authorization": f"Bearer {app_token}",
        "Accept": "application/vnd.github+json",
    }
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"https://api.github.com/app/installations/{installation_id}/access_tokens",
            headers=headers,
        )
        r.raise_for_status()
        return r.json()["token"]


async def get_app_installation_repository_forks(app_installation_token: str) -> list[dict[str, Any]]:
    headers = {
        "Authorization": f"Bearer {app_installation_token}",
        "Accept": "application/vnd.github+json",
    }
    async with httpx.AsyncClient() as client:
        r = await client.get(
            f"https://api.github.com/repos/{env.GIT_UPSTREAM_OWNER}/{env.GIT_UPSTREAM_REPO}/forks",
            headers=headers,
        )
        r.raise_for_status()
        return r.json()


async def commit_and_create_pull_request(
    root_app_installation_token: str,
    app_installation_token: str,
    fork_owner: str,
    fork_name: str,
    new_branch: str,
    file_path: str,
    file_content: bytes,
    pr_title: str,
) -> str:
    root_auth_headers = {"Authorization": f"token {root_app_installation_token}"}
    auth_headers = {"Authorization": f"token {app_installation_token}"}
    meta_headers = {"Accept": "application/vnd.github+json"}

    root_headers = root_auth_headers | meta_headers
    headers = auth_headers | meta_headers

    async with httpx.AsyncClient() as client:
        # Get SHA of the data branch to create a new branch off of in the fork
        r = await client.get(
            f"https://api.github.com/repos/{env.GIT_UPSTREAM_OWNER}/{fork_name}/git/refs/heads/{env.GIT_UPSTREAM_DATA_BRANCH}",
            headers=headers,
        )
        r.raise_for_status()
        base_sha = r.json()["object"]["sha"]

        # Create a new branch in the fork
        r = await client.post(
            f"https://api.github.com/repos/{fork_owner}/{fork_name}/git/refs",
            headers=headers,
            json={"ref": f"refs/heads/{new_branch}", "sha": base_sha},
        )
        r.raise_for_status()

        # Commit file contents to the new branch
        r = await client.put(
            f"https://api.github.com/repos/{fork_owner}/{fork_name}/contents/{file_path}",
            headers=headers,
            json={
                "message": f"Add {file_path}",
                "content": base64.b64encode(file_content).decode("utf-8"),
                "branch": new_branch,
            },
        )
        r.raise_for_status()
        commit_hash: str = r.json()["commit"]["sha"]

        # Open PR against upstream
        r = await client.post(
            f"https://api.github.com/repos/{env.GIT_UPSTREAM_OWNER}/{env.GIT_UPSTREAM_REPO}/pulls",
            headers=root_headers,
            json={
                "title": pr_title,
                "head": f"{fork_owner}:{new_branch}",
                "head_repo": fork_name,
                "base": env.GIT_UPSTREAM_DATA_BRANCH,
                "maintainer_can_modify": False,
            },
        )
        r.raise_for_status()

    return commit_hash
