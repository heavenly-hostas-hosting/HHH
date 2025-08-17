from pathlib import Path

from . import utils

CLIENT_ID = utils.assure_get_env("CLIENT_ID")
CLIENT_SECRET = utils.assure_get_env("CLIENT_SECRET")
PRIVATE_KEY = Path("pydis-cj12-heavenly-hostas-app.private-key.pem").read_text().strip()

SUPABASE_PUBLIC_URL = utils.assure_get_env("SUPABASE_PUBLIC_URL")
SUPABASE_INTERNAL_URL = utils.assure_get_env("SUPABASE_INTERNAL_URL")
SUPABASE_KEY = utils.assure_get_env("ANON_KEY")

JWT_SECRET = utils.assure_get_env("JWT_SECRET")
