#
# public_router.py - DeGirum Zoo Server: public API routes
# Copyright DeGirum Corp. 2024
#
# Implements DeGirum Zoo Server public API routes
#


from typing import Dict, List
from fastapi.responses import FileResponse
from fastapi import (
    APIRouter,
    Depends,
    Path,
    Header,
    Query,
    File,
    UploadFile,
)
from .internals import (
    PythonModelParams,
    ZooInfo,
    ModelInfo,
    Token,
    tokenManager,
    zooManager,
)


router = APIRouter(tags=["public"])


###################################################
# Token API
#


@router.get(
    "/tokens",
    summary="Get token",
    response_model=Token,
)
async def token_get(
    token: str = Header(description="Token to query"),
):
    return await tokenManager.verify_token(token)


@router.post(
    "/tokens",
    summary="Create new token",
    response_model=Token,
)
async def create_token(
    is_admin: bool = Query(description="Request admin access", default=False),
    token: str = Header(description="Token value", default=""),
):
    return await tokenManager.create_token(token, is_admin)


@router.delete(
    "/tokens",
    summary="Delete token",
    dependencies=[Depends(tokenManager.verify_token_admin)],
    response_model=Token,
)
async def delete_token(
    token_to_delete: str = Header(description="Token to delete"),
):
    return await tokenManager.delete_token(token_to_delete)


@router.post(
    "/tokens/{organization}/{zoo_name}",
    summary="Add zoo access to token",
    dependencies=[Depends(tokenManager.verify_token_admin)],
    response_model=Token,
)
async def token_add_zoo(
    organization: str,
    zoo_name: str,
    token_to_modify: str = Header(description="Token to modify"),
):
    return await tokenManager.add_zoo_access(
        token_to_modify, f"{organization}/{zoo_name}"
    )


@router.delete(
    "/tokens/{organization}/{zoo_name}",
    summary="Remove zoo access from token",
    dependencies=[Depends(tokenManager.verify_token_admin)],
    response_model=Token,
)
async def token_remove_zoo(
    organization: str,
    zoo_name: str,
    token_to_modify: str = Header(description="Token to modify"),
):
    return await tokenManager.remove_zoo_access(
        token_to_modify, f"{organization}/{zoo_name}"
    )


###################################################
# Zoo API
#


@router.get(
    "/zoos/{organization}",
    summary="Query the list of all model zoo URLs available to operate for the current user in given organization",
    response_model=List[ZooInfo],
)
async def list_zoos(organization: str, token: str = Header(description="Token value")):
    token_entry = await tokenManager.verify_token(token)
    all_org_zoos = await zooManager.list_zoos(organization=organization)
    return [
        zoo
        for zoo in all_org_zoos
        if token_entry.value.is_admin or zoo.url in token_entry.value.zoos
    ]


@router.get(
    "/models/{organization}/{zoo_name}",
    summary="Query the list of models and their attributes available in the given model zoo",
    dependencies=[Depends(tokenManager.verify_token_org_and_zoo)],
    response_model=Dict[str, PythonModelParams],
)
async def list_models(organization: str, zoo_name: str):
    return await zooManager.list_models(organization=organization, zoo_name=zoo_name)


@router.get(
    "/models/{organization}/{zoo_name}/{model}/check",
    summary="Check if model has specified checksum",
    dependencies=[Depends(tokenManager.verify_token_org_and_zoo)],
    response_model=Dict[str, bool],
    responses={
        200: {
            "description": "Success",
            "content": {
                "application/json": {
                    "example": {"status": True},
                },
            },
        }
    },
)
async def check_model(
    organization: str,
    zoo_name: str,
    model: str = Path(description="Model name"),
    checksum: str = Query(description="Model checksum to check if model matches"),
):
    return await zooManager.check_model(organization, zoo_name, model, checksum)


@router.get(
    "/models/{organization}/{zoo_name}/{model}/dictionary",
    summary="Get model labels dictionary",
    dependencies=[Depends(tokenManager.verify_token_org_and_zoo)],
    response_model=Dict[str, str],
    responses={
        200: {
            "description": "Success",
            "content": {
                "application/json": {
                    "example": {"0": "background", "1": "cat", "2": "dog"},
                },
            },
        }
    },
)
async def model_dictionary(
    organization: str,
    zoo_name: str,
    model: str = Path(description="Model name"),
):
    return await zooManager.model_dictionary(organization, zoo_name, model)


@router.get(
    "/models/{organization}/{zoo_name}/{model}/readme",
    summary="Get model readme",
    dependencies=[Depends(tokenManager.verify_token_org_and_zoo)],
    response_model=str,
)
async def model_readme(
    organization: str,
    zoo_name: str,
    model: str = Path(description="Model name"),
):
    return await zooManager.model_readme(organization, zoo_name, model)


@router.get(
    "/models/{organization}/{zoo_name}/{model}/info",
    summary="Get model info",
    dependencies=[Depends(tokenManager.verify_token_org_and_zoo)],
    response_model=ModelInfo,
)
async def model_params(
    organization: str,
    zoo_name: str,
    model: str = Path(description="Model name"),
):
    return await zooManager.model_params(organization, zoo_name, model)


@router.get(
    "/models/{organization}/{zoo_name}/{model}",
    summary="Download model from the given model zoo",
    dependencies=[Depends(tokenManager.verify_token_org_and_zoo)],
    response_class=FileResponse,
)
async def download_model(
    organization: str = Path(description="Organization name"),
    zoo_name: str = Path(description="Zoo name"),
    model: str = Path(description="Model name"),
):
    return await zooManager.download_model(organization, zoo_name, model)


@router.post(
    "/models/{organization}/{zoo_name}",
    status_code=201,
    summary="Upload model to the model zoo",
    dependencies=[Depends(tokenManager.verify_token_admin)],
    responses={
        201: {
            "description": "Upload model",
            "content": {"application/json": {"example": "organization/zoo/model"}},
        }
    },
)
async def upload_model(
    organization: str = Path(description="Organization name"),
    zoo_name: str = Path(description="Zoo name"),
    file: UploadFile = File(..., description="Model file to upload"),
    allow_overwrite: bool = Query(default=False, description="Allow model overwrite"),
) -> Dict[str, str]:
    return await zooManager.upload_model(
        organization=organization,
        zoo_name=zoo_name,
        file=file,
        allow_overwrite=allow_overwrite,
    )


@router.delete(
    "/models/{organization}/{zoo_name}/{model}",
    summary="Delete model from the model zoo",
    dependencies=[Depends(tokenManager.verify_token_admin)],
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": {
                        "url": "model URL string",
                    }
                }
            },
        },
    },
)
async def delete_model(
    organization: str = Path(description="Organization name"),
    zoo_name: str = Path(description="Zoo name"),
    model: str = Path(description="Model name"),
):
    return await zooManager.delete_model(organization, zoo_name, model)
