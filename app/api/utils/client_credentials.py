import os
from typing import Optional

from fastapi.exceptions import HTTPException
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.requests import Request
from fastapi.security import OAuth2
from fastapi.security.utils import get_authorization_scheme_param
from starlette.status import HTTP_401_UNAUTHORIZED



class Oauth2ClientCredentials(OAuth2):
    def __init__(
        self,
        tokenUrl: str,
        scheme_name: str = None,
        scopes: dict = None,
        auto_error: bool = True,
    ):
        if not scopes:
            scopes = {}
        flows = OAuthFlowsModel(
            clientCredentials={"tokenUrl": tokenUrl, "scopes": scopes}
        )
        super().__init__(
            flows=flows, scheme_name=scheme_name, auto_error=auto_error
        )

    async def __call__(self, request: Request) -> Optional[str]:
        if os.getenv("YOUR_ENV") == "testing":
            return "mocked_token"
        authorization: str = request.headers.get("Authorization")

        if authorization is None:
            if self.auto_error:
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            return

        scheme, param = get_authorization_scheme_param(authorization)

        if scheme.lower() != "bearer" or not param:
            if self.auto_error:
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            return None
        return param


oauth2_scheme = Oauth2ClientCredentials(tokenUrl="https://simulations.auth.us-west-2.amazoncognito.com/oauth2/token")
