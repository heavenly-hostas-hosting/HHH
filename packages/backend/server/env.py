from . import utils

CLIENT_ID = utils.assure_get_env("CLIENT_ID")
CLIENT_SECRET = utils.assure_get_env("CLIENT_SECRET")
# SUPABASE_URL = utils.assure_get_env("SUPABASE_PUBLIC_URL")
SUPABASE_INTERNAL_URL = "http://kong:8000"
SUPABASE_EXTERNAL_URL = "http://localhost:8000"
SUPABASE_KEY = utils.assure_get_env("ANON_KEY")

JWT_SECRET = utils.assure_get_env("JWT_SECRET")
