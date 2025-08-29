from fastapi import APIRouter, status

healthcheck_router = APIRouter()


@healthcheck_router.get("/healthcheck", status_code=status.HTTP_200_OK)
async def healthcheck():
    return None
