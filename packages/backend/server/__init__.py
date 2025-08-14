import secrets
from typing import Annotated

import httpx
import jwt
from fastapi import FastAPI, HTTPException, Query, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.routing import APIRouter
from gotrue import CodeExchangeParams, SignInWithOAuthCredentials, SignInWithOAuthCredentialsOptions

from . import env, sb

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://*.github.com", "http://localhost:9000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/auth")
async def auth(  # noqa: D103
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

    response = RedirectResponse("https://github.com/Matiiss/pydis-cj12-heavenly-hostas")

    response.set_cookie(
        key=sb.ACCESS_TOKEN_COOKIE_KEY,
        value=gh_response.session.access_token,
        httponly=True,
        secure=True,
        samesite="none",
    )
    response.set_cookie(
        key=sb.REFRESH_TOKEN_COOKIE_KEY,
        value=gh_response.session.refresh_token,
        httponly=True,
        secure=True,
        samesite="none",
    )

    return response


@app.get("/login")
async def login() -> RedirectResponse:  # noqa: D103
    sb_client = await sb.create_external_client()

    gh_response = await sb_client.auth.sign_in_with_oauth(
        SignInWithOAuthCredentials(
            provider="github",
            options=SignInWithOAuthCredentialsOptions(redirect_to="http://localhost:9000/auth"),
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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="localhost", port=8000, workers=1)
