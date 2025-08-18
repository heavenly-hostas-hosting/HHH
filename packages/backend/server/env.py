from pathlib import Path

from . import utils

CLIENT_ID = utils.assure_get_env("CLIENT_ID")
CLIENT_SECRET = utils.assure_get_env("CLIENT_SECRET")
PRIVATE_KEY = Path("pydis-cj12-heavenly-hostas-app.private-key.pem").read_text().strip()

SUPABASE_PUBLIC_URL = utils.assure_get_env("SUPABASE_PUBLIC_URL")
SUPABASE_INTERNAL_URL = utils.assure_get_env("SUPABASE_INTERNAL_URL")
SUPABASE_KEY = utils.assure_get_env("ANON_KEY")

GITHUB_CALLBACK_REDIRECT_URI = utils.assure_get_env("GITHUB_CALLBACK_REDIRECT_URI")
POST_AUTH_REDIRECT_URI = utils.assure_get_env("POST_AUTH_REDIRECT_URI")
# ADDITIONAL_REDIRECT_URLS = utils.assure_get_env("ADDITIONAL_REDIRECT_URLS").split(" ")
CORS_ALLOW_ORIGINS = utils.assure_get_env("CORS_ALLOW_ORIGINS").split(" ")

JWT_SECRET = utils.assure_get_env("JWT_SECRET")

GIT_UPSTREAM_OWNER = utils.assure_get_env("GIT_UPSTREAM_OWNER")
GIT_UPSTREAM_REPO = utils.assure_get_env("GIT_UPSTREAM_REPO")
GIT_UPSTREAM_DATA_BRANCH = utils.assure_get_env("GIT_UPSTREAM_DATA_BRANCH")
GIT_UPSTREAM_APP_INSTALLATION_ID = int(utils.assure_get_env("GIT_UPSTREAM_APP_INSTALLATION_ID"))
