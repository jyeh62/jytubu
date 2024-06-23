from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse, JSONResponse
from itsdangerous import URLSafeSerializer, BadSignature
from google_auth_oauthlib.flow import Flow
import os

from app.utils.token import save_credentials, load_credentials

auth_router = APIRouter()

# 환경 변수로부터 설정 값 로드
CLIENT_SECRETS_FILE = "config/client_secret.json"
REDIRECT_URI = os.getenv("AUTH_REDIRECT_URL", "http://localhost:8000/auth/callback") # "http://localhost:8000/auth/callback"
SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key")

flow = Flow.from_client_secrets_file(
    CLIENT_SECRETS_FILE,
    scopes=["https://www.googleapis.com/auth/youtube.readonly"],
    redirect_uri=REDIRECT_URI
)

serializer = URLSafeSerializer(SECRET_KEY)

@auth_router.get("/auth")
def auth(request: Request):
    print(f'auth: secret_key {SECRET_KEY}, redirect_url: {REDIRECT_URI}')
    credentials = load_credentials()
    if credentials and credentials.valid:
        return RedirectResponse(url="/subscriptions")
    elif credentials and credentials.expired and credentials.refresh_token:
        credentials.refresh(httpx.AsyncClient())
        save_credentials(credentials)
        return RedirectResponse(url="/subscriptions")
    else:
        authorization_url, state = flow.authorization_url()
        request.session['state'] = serializer.dumps(state)
        return RedirectResponse(authorization_url)

@auth_router.get("/auth/callback")
def callback(request: Request):
    state = request.query_params.get('state', '')
    try:
        stored_state = serializer.loads(request.session.pop('state', ''))
    except BadSignature:
        return JSONResponse(content={"error": "Invalid state parameter"}, status_code=400)
    
    if state != stored_state:
        return JSONResponse(content={"error": "State mismatch error"}, status_code=400)
    
    flow.fetch_token(authorization_response=str(request.url))
    credentials = flow.credentials
    save_credentials(credentials)

    return RedirectResponse(url="/subscriptions")
