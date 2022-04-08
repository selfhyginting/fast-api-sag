from fastapi_jwt_auth import AuthJWT
from pydantic import BaseModel

# tokenization
class Settings(BaseModel):
    authjwt_secret_key:str='8f585b4ac7a1e1f76af9584e784b67089fe5ad9892876dde9273179d5de06a34'

@AuthJWT.load_config
def get_config():
    return Settings()