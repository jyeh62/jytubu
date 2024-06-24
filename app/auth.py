from fastapi import APIRouter, Request, status, Response
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from itsdangerous import URLSafeSerializer, BadSignature
from google_auth_oauthlib.flow import Flow
import os
from pydantic import BaseModel


from app.utils.token import save_credentials, load_credentials

auth_router = APIRouter()
templates = Jinja2Templates(directory="templates")


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

class UserInfo(BaseModel):
    name: str
    token: str

@auth_router.get("/login")
def login(token: str, name: str, response: Response):
    userInfo = UserInfo(name=name, token=token)
    print(f'request login: {UserInfo}')
    credentials = load_credentials(filepath=token)
    if credentials and credentials.valid:
        return {"login" : credentials.token}
    else:
        auth_router.userInfo = userInfo
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"login" : "fail"}
        # return RedirectResponse(url="/auth", status_code=status.HTTP_303_SEE_OTHER)

@auth_router.get("/auth")
def auth(request: Request):
    print(f'auth: secret_key {SECRET_KEY}, redirect_url: {REDIRECT_URI}')
    print(f'request login: {auth_router.userInfo.name}, {auth_router.userInfo.token}')
    credentials = load_credentials(auth_router.userInfo.token)
    if credentials and credentials.valid:
        return RedirectResponse(url="/subscriptions")
    elif credentials and credentials.expired and credentials.refresh_token:
        credentials.refresh(httpx.AsyncClient())
        save_credentials(credentials, filepath=credentials.token)
        return RedirectResponse(url="/subscriptions")
    else:
        authorization_url, state = flow.authorization_url()
        request.session['state'] = serializer.dumps(state)
        return RedirectResponse(authorization_url)

@auth_router.get("/auth/callback")
def callback(request: Request):
    print('call /auth/callback')
    state = request.query_params.get('state', '')
    try:
        stored_state = serializer.loads(request.session.pop('state', ''))
    except BadSignature:
        return JSONResponse(content={"error": "Invalid state parameter"}, status_code=400)
    
    if state != stored_state:
        return JSONResponse(content={"error": "State mismatch error"}, status_code=400)
    
    flow.fetch_token(authorization_response=str(request.url))
    credentials = flow.credentials
    save_credentials(credentials, filepath=credentials.token)

    #return {"login" : credentials.token}
    print(f'/auth/callback success {credentials.token}')
    print(f'myapp://login?token={credentials.token}')
    auth_result = {
        "url" : f'myapp://login?token={credentials.token}',
        
    }
    return templates.TemplateResponse("redirect.html", context={"request": request, **auth_result})

