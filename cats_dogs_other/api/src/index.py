import io
import logging
import os # this line is new

from fastapi import FastAPI, UploadFile, Depends # here, we add Depends
from fastapi.security import OAuth2PasswordBearer # this line is new
from kto.inference import Inference
from oidc_jwt_validation.authentication import Authentication # this line is new
from oidc_jwt_validation.http_service import ServiceGet # this line is new

app = FastAPI()
model = Inference("./cats_dogs_other/api/resources/model.h5")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token") # this scheme comes from FastAPI. It allows to check some token information and give the token to the function

issuer = os.getenv("OAUTH2_ISSUER") # This is a value from an environment variable. It allows us to not hard code some information
audience = os.getenv("OAUTH2_AUDIENCE") # this line is new
jwks_uri = os.getenv("OAUTH2_JWKS_URI") # this line is new
logger = logging.getLogger(__name__) # this line is new
authentication = Authentication(logger, issuer, ServiceGet(logger), jwks_uri) # This object will check deeper the validity of the token
skip_oidc = False # this boolean will be used for tests purproses. By default and in production, it will be always False


@app.get("/health") # Note that this line does not change. It will not be protected
def health():
    return {"status": "OK"}


@app.post("/upload")
async def upload(file: UploadFile, token: str = Depends(oauth2_scheme)): # Take a look at this new token argument
    if not skip_oidc:
        await authentication.validate_async(token, audience, "get::prediction") # This function will validate the token
    file_readed = await file.read()
    file_bytes = io.BytesIO(file_readed)
    return model.execute(file_bytes)
