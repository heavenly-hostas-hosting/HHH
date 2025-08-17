from fastapi import HTTPException, Request, Response
from gotrue.constants import STORAGE_KEY
from gotrue.errors import AuthSessionMissingError
from gotrue.types import UserIdentity
from supabase import AsyncClient, AsyncClientOptions, create_async_client

from . import env

ACCESS_TOKEN_COOKIE_KEY = "sb_access_token"  # noqa: S105
REFRESH_TOKEN_COOKIE_KEY = "sb_refresh_token"  # noqa: S105
CODE_VERIFIER_COOKIE_KEY = "sb_code_verifier"


def set_response_token_cookies_(response: Response, access_token: str, refresh_token: str) -> None:
    response.set_cookie(
        key=ACCESS_TOKEN_COOKIE_KEY,
        value=access_token,
        httponly=True,
        secure=True,
        samesite="none",
    )
    response.set_cookie(
        key=REFRESH_TOKEN_COOKIE_KEY,
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="none",
    )


async def create_internal_client() -> AsyncClient:
    """Create a Supabase client."""
    return await create_async_client(
        supabase_url=env.SUPABASE_INTERNAL_URL,
        supabase_key=env.SUPABASE_KEY,
        options=AsyncClientOptions(flow_type="pkce"),
    )


async def create_public_client() -> AsyncClient:
    """Create a Supabase client."""
    return await create_async_client(
        supabase_url=env.SUPABASE_PUBLIC_URL,
        supabase_key=env.SUPABASE_KEY,
        options=AsyncClientOptions(flow_type="pkce"),
    )


async def get_code_verifier_from_client(client: AsyncClient) -> str:
    """Get the code verifier from the client."""
    storage = client.auth._storage  # noqa: SLF001
    code_verifier = await storage.get_item(f"{STORAGE_KEY}-code-verifier")

    if code_verifier is None:
        raise HTTPException(status_code=401, detail="Code verifier not found in storage")

    return code_verifier


async def get_session(request: Request) -> AsyncClient:
    """Get a Supabase client session."""
    access_token = request.cookies.get(ACCESS_TOKEN_COOKIE_KEY)
    refresh_token = request.cookies.get(REFRESH_TOKEN_COOKIE_KEY)

    if access_token is None or refresh_token is None:
        raise HTTPException(status_code=401, detail="No session tokens found")

    client = await create_internal_client()
    await client.auth.set_session(access_token=access_token, refresh_token=refresh_token)

    return client


async def get_github_identity(client: AsyncClient) -> UserIdentity:
    user_identities = await client.auth.get_user_identities()
    if isinstance(user_identities, AuthSessionMissingError):
        raise HTTPException(status_code=401, detail="User not authenticated")

    for identity in user_identities.identities:
        if identity.provider == "github":
            gh_identity = identity
            break
    else:
        raise HTTPException(status_code=401, detail="GitHub identity not found... how did you get here?")

    return gh_identity
