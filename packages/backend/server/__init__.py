import secrets
from datetime import datetime
from typing import Annotated

from fastapi import FastAPI, HTTPException, Query, Request, Response, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from gotrue import CodeExchangeParams, SignInWithOAuthCredentials, SignInWithOAuthCredentialsOptions
from pydantic import BaseModel

from . import env, gh, pg, sb

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=env.ADDITIONAL_REDIRECT_URLS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/login")
async def login() -> RedirectResponse:
    sb_client = await sb.create_public_client()

    gh_response = await sb_client.auth.sign_in_with_oauth(
        SignInWithOAuthCredentials(
            provider="github",
            options=SignInWithOAuthCredentialsOptions(redirect_to=env.GITHUB_CALLBACK_REDIRECT_URI),
        ),
    )

    response = RedirectResponse(gh_response.url)
    response.set_cookie(
        key=sb.CODE_VERIFIER_COOKIE_KEY,
        value=await sb.get_code_verifier_from_client(sb_client),
        httponly=True,
        secure=True,
        samesite="lax",
    )
    return response


@app.get("/logout")
async def logout(request: Request) -> RedirectResponse:
    sb_client = await sb.get_session(request)

    await sb_client.auth.sign_out()

    response = RedirectResponse(env.POST_AUTH_REDIRECT_URI)
    response.delete_cookie(
        key=sb.ACCESS_TOKEN_COOKIE_KEY,
        httponly=True,
        secure=True,
        samesite="lax",
    )
    response.delete_cookie(
        key=sb.REFRESH_TOKEN_COOKIE_KEY,
        httponly=True,
        secure=True,
        samesite="lax",
    )
    return response


@app.get("/auth")
async def auth(
    code: Annotated[str, Query()],
    request: Request,
) -> RedirectResponse:
    client = await sb.create_internal_client()
    code_verifier = request.cookies.get(sb.CODE_VERIFIER_COOKIE_KEY)
    if code_verifier is None:
        raise HTTPException(status_code=401, detail="Code verifier not found in cookies")

    gh_response = await client.auth.exchange_code_for_session(
        CodeExchangeParams(
            code_verifier=code_verifier,
            auth_code=code,
            redirect_to="",
        ),
    )

    if gh_response.session is None:
        raise HTTPException(status_code=401, detail="Failed to exchange code for session")

    response = RedirectResponse(env.POST_AUTH_REDIRECT_URI)
    response.delete_cookie(
        key=sb.CODE_VERIFIER_COOKIE_KEY,
        httponly=True,
        secure=True,
        samesite="lax",
    )
    sb.set_response_token_cookies_(
        response,
        access_token=gh_response.session.access_token,
        refresh_token=gh_response.session.refresh_token,
    )

    return response


@app.post("/publish")
async def publish(  # noqa: C901
    image: UploadFile,
    http_request: Request,
) -> Response:
    client = await sb.get_session(http_request)

    client_session = await client.auth.get_session()
    if client_session is None:
        raise HTTPException(status_code=401, detail="User not authenticated")

    gh_identity = await sb.get_github_identity(client)
    user_name = gh_identity.identity_data["user_name"]
    app_token = gh.get_app_token()

    installation_id: int | None = None
    for installation in await gh.get_app_installations(app_token):
        if installation["account"]["login"] == user_name:
            if installation_id is not None:
                raise HTTPException(status_code=400, detail="Multiple GitHub App installations found for user")

            installation_id = installation["id"]

    if installation_id is None:
        raise HTTPException(status_code=404, detail="No GitHub App installation found")

    app_installation_token = await gh.get_app_installation_token(installation_id, app_token)
    installation_repositories = await gh.get_app_installation_repositories(app_installation_token)

    total_repo_count = installation_repositories["total_count"]
    if total_repo_count == 0:
        raise HTTPException(status_code=409, detail="GitHub App not installed on any repository")
    elif total_repo_count > 1:
        raise HTTPException(status_code=409, detail="GitHub App must be installed on a single repository")

    root_app_installation_token = await gh.get_app_installation_token(env.GIT_UPSTREAM_APP_INSTALLATION_ID, app_token)
    all_fork_full_names = set(
        repo["full_name"] for repo in await gh.get_app_installation_repository_forks(root_app_installation_token)
    )
    repository = installation_repositories["repositories"][0]

    if not repository["fork"] or repository["full_name"] not in all_fork_full_names:
        raise HTTPException(
            status_code=409, detail="The installation repository must be a fork of the main repository"
        )

    now = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    random_sequence = secrets.token_hex(8)
    file_stem = f"{now}_{random_sequence}"
    file_name = f"{file_stem}.webp"

    commit_hash = await gh.commit_and_create_pull_request(
        root_app_installation_token=root_app_installation_token,
        app_installation_token=app_installation_token,
        fork_owner=user_name,
        fork_name=repository["name"],
        new_branch=file_stem,
        file_path=file_name,
        file_content=await image.read(),
        pr_title=f"Publish {file_name}",
    )
    await pg.github_files_insert_row(
        username=user_name,
        filename=file_name,
        commit_hash=commit_hash,
    )

    response = Response(content="Publish endpoint hit", status_code=200)
    sb.set_response_token_cookies_(
        response,
        access_token=client_session.access_token,
        refresh_token=client_session.refresh_token,
    )

    return response


class LoginStatusResponse(BaseModel):
    username: str | None
    logged_in: bool


@app.get("/status", response_model=LoginStatusResponse)
async def status(http_request: Request) -> JSONResponse:
    try:
        client = await sb.get_session(http_request)
        client_session = await client.auth.get_session()
        if client_session is None:
            raise HTTPException(status_code=401, detail="User not authenticated")

        gh_identity = await sb.get_github_identity(client)
    except HTTPException as e:
        if e.status_code != 401:
            raise

        return JSONResponse(
            content=LoginStatusResponse(
                username=None,
                logged_in=False,
            ).model_dump()
        )

    user_name = gh_identity.identity_data["user_name"]
    response = JSONResponse(
        content=LoginStatusResponse(
            username=user_name,
            logged_in=True,
        ).model_dump()
    )
    sb.set_response_token_cookies_(
        response,
        access_token=client_session.access_token,
        refresh_token=client_session.refresh_token,
    )

    return response


class VerifyPRResponse(BaseModel):
    is_valid: bool


@app.get("/verify_pr")
async def verify_pr(
    filename: Annotated[str, Query()],
    commit_hash: Annotated[str, Query()],
) -> VerifyPRResponse:
    is_valid = await pg.github_files_check_exists(
        filename=filename,
        commit_hash=commit_hash,
    )

    return VerifyPRResponse(is_valid=is_valid)


class ArtworksResponse(BaseModel):
    artworks: list[tuple[str, str]]


@app.get("/artworks")
async def artworks() -> ArtworksResponse:
    works = await pg.github_files_get_all()

    return ArtworksResponse(artworks=works)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="localhost", port=8000, workers=1)
