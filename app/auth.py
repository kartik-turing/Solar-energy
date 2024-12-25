import logging
from datetime import datetime, timezone

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jwt import (
    DecodeError,
    ExpiredSignatureError,
    InvalidAudienceError,
    InvalidIssuerError,
    decode,
)


try:
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="https://simulations.auth.us-west-2.amazoncognito.com/oauth2/token")
except:
    raise Exception("Token URL not found in Secrets")


def verify_token(token: str):
    try:
        try:
            decoded_token = decode(token, options={"verify_signature": False})
            payload = decoded_token
        except ExpiredSignatureError:
            raise HTTPException(
                status_code=401, detail="Invalid Token: Token has expired"
            )
        except InvalidAudienceError:
            raise HTTPException(
                status_code=401, detail="Invalid Token: incorrect audience"
            )
        except InvalidIssuerError:
            raise HTTPException(
                status_code=401, detail="Invalid Token: incorrect issuer"
            )
        except DecodeError:
            raise HTTPException(status_code=401, detail="Invalid Token")
        except Exception as e:
            raise HTTPException(
                status_code=401, detail=f"Token verification failed: {str(e)}"
            )
        if (
            payload.get("client_id") != "5ubsfje53f99m0pmgk9chq2vte"
        ):
            logging.error("Invalid Token: Incorrect client id")
            raise HTTPException(
                status_code=401,
                detail="Invalid Token: Incorrect client id",
            )
        #
        if payload.get("scope") != "simulations/simulations":
            logging.error("Invalid Token: Incorrect audience")
            raise HTTPException(
                status_code=401,
                detail="Invalid Token: Incorrect audience",
            )

        # Verify the issuer
        if payload.get("iss") != "https://cognito-idp.us-west-2.amazonaws.com/us-west-2_jbDKjsa0K":
            logging.error("Invalid Token: Incorrect issuer")
            raise HTTPException(
                status_code=401,
                detail="Invalid Token: Incorrect issuer",
            )

        # Verify the expiration
        exp = payload.get("exp")
        if exp is None or datetime.fromtimestamp(
            exp, timezone.utc
        ) < datetime.now(timezone.utc):
            logging.error("Invalid Token: Token has expired")
            raise HTTPException(
                status_code=401,
                detail="Invalid Token: Token has expired",
            )

        # Verify other claims
        if not payload.get("sub"):
            logging.error("Invalid Token: Subject claim is missing")
            raise HTTPException(
                status_code=401,
                detail="Invalid Token: Subject claim is missing",
            )

    except Exception as exception:
        logging.error(
            f"An error occured while validating token: {str(exception)}"
        )
        raise HTTPException(
            status_code=401,
            detail="Invalid Token",
        )


def authenticate_current_user(token: str = Depends(oauth2_scheme)):
    return verify_token(token)
