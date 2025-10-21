from app.dependencies import check_license
from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/account", tags=["account"])


@router.get("/login/")
async def login_get(
    username: str = Query(...),
    password: str = Query(...),
    _: None = Depends(check_license),
):

    if username == "admin" and password == "admin":
        return JSONResponse(
            {
                "username": username,
                "token": "<token>",
            },
        )

    return JSONResponse(
        {
            "message": "Invalid password",
        },
        status_code=401,
    )
