#
# internals.py - DeGirum Zoo Server: internal implementation
# Copyright DeGirum Corp. 2024
#
# Contains DeGirum Zoo Server internal implementation details
#

from pydantic import BaseModel, Field, ConfigDict
from fastapi import Header, Path, UploadFile, Request, status, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.encoders import jsonable_encoder
from starlette.background import BackgroundTask
import asyncio
import dataclasses
import aiorwlock
import aiofiles.os
import pathlib
import json
import os
from copy import deepcopy
import base58
from uuid import uuid4
from typing import Dict, Any, List, Optional
import zipfile


# Model params representation
PythonModelParams = Dict[str, Any]


class GeneralError(BaseModel):
    """General error type definition"""

    detail: str


class ZooInfo(BaseModel):
    """List zoo data model"""

    name: str = Field(description="Model Zoo name")
    url: str = Field(description="Model Zoo URL")
    public: bool = Field(description="Is zoo public flag")
    own: bool = Field(description="Is this zoo owned by ths organization")


class ModelInfo(BaseModel):
    """Model info representation"""

    model_config = ConfigDict(protected_namespaces=())

    model_params: PythonModelParams = Field(
        description="Model parameters dictionary", default={}
    )
    model_dictionary: Dict[str, Any] = Field(
        description="Model class label dictionary", default={}
    )
    readme: str = Field(description="Model readme file contents", default="")
    crc: str = Field(description="Model checksum", default="")


@dataclasses.dataclass
class TokenValue:
    """Token entry class"""

    is_admin: bool = False
    zoos: List[str] = dataclasses.field(default_factory=list)


@dataclasses.dataclass
class Token:
    token: str = ""
    value: TokenValue = dataclasses.field(default_factory=TokenValue)


async def my_to_thread(func, /, *args, **kwargs):
    """Asynchronously run function *func* in a separate thread.

    Any *args and **kwargs supplied for this function are directly passed
    to *func*. Also, the current :class:`contextvars.Context` is propagated,
    allowing context variables from the main thread to be accessed in the
    separate thread.

    Return a coroutine that can be awaited to get the eventual result of *func*.
    """
    import functools
    import contextvars

    loop = asyncio.events.get_running_loop()
    ctx = contextvars.copy_context()
    func_call = functools.partial(ctx.run, func, *args, **kwargs)
    return await loop.run_in_executor(None, func_call)


class TokenManager:
    """Token manager class"""

    def __init__(self):
        self._lock = aiorwlock.RWLock()
        self._json_path: Optional[pathlib.Path] = None
        self._tokens: Dict[str, TokenValue] = {}

    async def load(self, zoo_root: pathlib.Path):
        """Load token data from file"""

        self._json_path = zoo_root / "tokens.json"

        try:
            async with aiofiles.open(self._json_path, "r") as f:
                raw_json = json.loads(await f.read())
            self._tokens = {
                k: TokenValue(is_admin=v["is_admin"], zoos=v["zoos"])
                for k, v in raw_json.items()
            }
        except:
            pass  # ignore all errors

    async def create_token(self, token: str, is_admin: bool) -> Token:
        """Create token

        - `token`: requestor token value (should have admin rights)
        - `is_admin`: to create new token with admin rights
        """
        async with self._lock.writer:

            # we allow creating token only if there is no tokens (fresh install) or bearer token has admin rights
            if self._tokens:
                token_entry = self._tokens.get(token) if token else None
                if token_entry is None or not token_entry.is_admin:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Token does not have admin rights",
                    )
            else:
                if not is_admin:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="First token should be created with admin rights",
                    )

            ORIG_LEN = 27
            ENCODED_LEN = 37
            rnd = os.urandom(ORIG_LEN)
            encoded = base58.b58encode(rnd).decode()
            token_str = "dg_" + "_" * (ENCODED_LEN - len(encoded)) + encoded

            new_token_entry = TokenValue(is_admin=is_admin)
            self._tokens[token_str] = new_token_entry
            await self._save()
            return Token(token_str, deepcopy(new_token_entry))

    async def delete_token(self, token: str) -> Token:
        """Delete token"""
        async with self._lock.writer:
            token_entry = self._tokens.get(token)
            if token_entry is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Token does not exist",
                )
            del self._tokens[token]
            await self._save()
            return Token(token, deepcopy(token_entry))

    async def add_zoo_access(self, token: str, zoo_url: str) -> Token:
        """Add zoo to token"""
        async with self._lock.writer:
            token_entry = self._tokens.get(token)
            if token_entry is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Token does not exist",
                )
            if zoo_url not in token_entry.zoos:
                token_entry.zoos.append(zoo_url)
                token_entry.zoos.sort()
                await self._save()
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Nothing to add: token already has access to {zoo_url}",
                )
            return Token(token, deepcopy(token_entry))

    async def remove_zoo_access(self, token: str, zoo_url: str) -> Token:
        """Remove zoo from token"""
        async with self._lock.writer:
            token_entry = self._tokens.get(token)
            if token_entry is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Token does not exist",
                )
            if zoo_url in token_entry.zoos:
                token_entry.zoos.remove(zoo_url)
                await self._save()
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Nothing to remove: token already does not have access to {zoo_url}",
                )
            return Token(token, deepcopy(token_entry))

    async def verify_token(
        self,
        token: str = Header(description="Token value"),
    ) -> Token:
        """Verify token for read access"""
        return await self._verify_token_impl(token)

    async def verify_token_admin(
        self,
        token: str = Header(description="Token value"),
    ) -> Token:
        """Verify token for admin access"""
        return await self._verify_token_impl(token, need_admin=True)

    async def verify_token_org_and_zoo(
        self,
        organization: str = Path(description="Organization name"),
        zoo_name: str = Path(description="Zoo name"),
        token: str = Header(description="Token value"),
    ) -> Token:
        """Verify token, and zoo access rights"""
        token_obj = await self._verify_token_impl(token)
        zoo_url = f"{organization}/{zoo_name}"
        if not token_obj.value.is_admin and zoo_url not in token_obj.value.zoos:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Token does not have access rights to zoo {zoo_url}",
            )
        return token_obj

    async def _verify_token_impl(
        self,
        token: str,
        need_admin: bool = False,
    ) -> Token:
        """Verify token

        - `token`: token value
        - `need_admin`: admin rights flag to check against

        Returns a deep copy of a token entry object if token is valid, raises HTTP exception 401 otherwise
        """
        async with self._lock.reader:
            token_entry = self._tokens.get(token)
            if token_entry is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token is not valid",
                )

            if need_admin and not token_entry.is_admin:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token does not have admin rights",
                )

            return Token(token, deepcopy(token_entry))

    async def _save(self):
        """Save token data to file"""
        if self._json_path is not None:
            async with aiofiles.open(self._json_path, "w") as f:
                await f.write(
                    json.dumps(
                        self._tokens, indent=2, default=lambda d: dataclasses.asdict(d)
                    )
                )


# Token manager instance
tokenManager = TokenManager()


class ModelZoo:
    """Model zoo handling class"""

    def __init__(self, zoo_root: pathlib.Path, organization: str, zoo_name: str):
        self._organization = organization
        self._zoo_name = zoo_name
        self._zoo_root = zoo_root / organization / zoo_name

    async def load(self):
        self._models = await self._scan_models()

    def extract_model_info(
        self, model: pathlib.Path, raise_exception_on_error: bool
    ) -> Optional[ModelInfo]:
        """Extract model info from model zip archive"""

        if not model.is_file() or model.suffix != ZooManager.model_ext:
            if raise_exception_on_error:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Model archive {model} is not a valid zip archive",
                )
            else:
                return None  # skip non-model files

        model_name = model.stem
        model_params = {}
        model_dictionary = {}
        readme = ""
        crc = ""

        with zipfile.ZipFile(model, "r") as zip_ref:
            file_list = zip_ref.namelist()

            model_param_file = [
                file
                for file in file_list
                if pathlib.Path(file).name == f"{model_name}.json"
            ]
            if not model_param_file:
                if raise_exception_on_error:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Model archive {model} does not contain model parameter file",
                    )
                else:
                    return None  # skip model if no model parameter file found

            # load model parameters file
            with zip_ref.open(model_param_file[0]) as param_file:
                model_params = json.load(param_file)

            # get model checksum
            if not "Checksum" in model_params:
                if raise_exception_on_error:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Model archive {model} does not contain model checksum",
                    )
                else:
                    return None  # skip model if no checksum found
            crc = model_params["Checksum"]

            # load model labels file, if any
            if (
                "POST_PROCESS" in model_params
                and "LabelsPath" in model_params["POST_PROCESS"][0]
            ):
                labels_file = [
                    file
                    for file in file_list
                    if pathlib.Path(file).name
                    == model_params["POST_PROCESS"][0]["LabelsPath"]
                ]
                if labels_file:
                    with zip_ref.open(labels_file[0]) as file:
                        model_dictionary = json.load(file)

            # load readme file, if any
            readme_file = [
                file
                for file in file_list
                if pathlib.Path(file).name.lower() == "readme.md"
            ]
            if readme_file:
                with zip_ref.open(readme_file[0]) as file:
                    readme = file.read().decode()

        return ModelInfo(
            model_params=model_params,
            model_dictionary=model_dictionary,
            readme=readme,
            crc=crc,
        )

    async def _scan_models(self) -> Dict[str, ModelInfo]:
        """Scan models in zoo"""
        models: Dict[str, ModelInfo] = {}

        for model in self._zoo_root.iterdir():
            info = await my_to_thread(
                self.extract_model_info, model, raise_exception_on_error=False
            )
            if info:
                models[model.stem] = info
        return models

    def info(self) -> ZooInfo:
        """Return zoo info"""
        return ZooInfo(
            name=self._zoo_name,
            url=f"{self._organization}/{self._zoo_name}",
            public=False,
            own=False,
        )

    def list_models(self) -> Dict[str, PythonModelParams]:
        """List models in zoo"""
        return {name: info.model_params for name, info in self._models.items()}

    def get_model(self, model: str) -> ModelInfo:
        """Get model info"""

        info = self._models.get(model)
        if info is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Model {model} is not found in model zoo {self._organization}/{self._zoo_name}",
            )
        return info


class ZooManager:
    """Zoo manager class"""

    model_ext = ".zip"  # model file extension
    temp_subdir = "__dg_zoo_server_temp__"  # temporary directory name

    def __init__(self):
        self._zoo_root: Optional[pathlib.Path] = None
        self._lock = aiorwlock.RWLock()
        self._zoos: Dict[str, ModelZoo] = {}

    async def load(self, zoo_root: pathlib.Path):
        """Load zoo data from filesystem"""
        self._zoo_root = zoo_root
        self._zoos = await self._scan_zoos()

        # create temporary directory if not exists
        temp_dir = self.temp_path()
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)

    def temp_path(self) -> pathlib.Path:
        """Return temporary path"""
        assert self._zoo_root is not None
        return self._zoo_root / self.temp_subdir

    async def _scan_zoos(self) -> Dict[str, ModelZoo]:
        """Scan zoo directories"""

        zoos: Dict[str, ModelZoo] = {}
        if self._zoo_root is None:
            return zoos

        for organization in self._zoo_root.iterdir():
            if organization.name == self.temp_subdir:
                continue  # skip temporary directory
            if organization.is_dir():
                for zoo in organization.iterdir():
                    if zoo.is_dir():
                        mz = ModelZoo(self._zoo_root, organization.name, zoo.name)
                        await mz.load()
                        zoos[f"{organization.name}/{zoo.name}"] = mz

        return zoos

    def get_zoo(self, organization: str, zoo_name: str) -> ModelZoo:
        zoo_url = f"{organization}/{zoo_name}"
        zoo = self._zoos.get(zoo_url)
        if zoo is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Zoo {zoo_url} is not found",
            )
        return zoo

    async def list_zoos(self, *, organization: str) -> List[ZooInfo]:
        """Return zoo list for given organization"""
        async with self._lock.reader:
            return [
                zoo.info()
                for zoo in self._zoos.values()
                if zoo._organization == organization
            ]

    async def list_models(
        self, *, organization: str, zoo_name: str
    ) -> Dict[str, PythonModelParams]:
        """Query the list of models and their attributes available in the given model zoo

        - `organization`: Organization name
        - `zoo_name`: Zoo name
        """
        async with self._lock.reader:
            return self.get_zoo(organization, zoo_name).list_models()

    async def check_model(
        self, organization: str, zoo_name: str, model: str, checksum: str
    ) -> Dict[str, bool]:
        """Verify model checksum

        - `organization`: Organization name
        - `zoo_name`: Zoo name
        - `model`: Model name
        - `checksum`: path to model temporary file

        Returns dictionary with verification status: {"status": True/False}
        """
        async with self._lock.reader:
            model_info = self.get_zoo(organization, zoo_name).get_model(model)
            return {"status": model_info.crc == checksum}

    async def model_dictionary(
        self,
        organization: str,
        zoo_name: str,
        model: str,
    ) -> Dict[str, str]:
        """Get model labels dictionary for model from the given model zoo

        - `organization`: Organization name
        - `zoo_name`: Zoo name
        - `model`: Model name
        """
        async with self._lock.reader:
            model_info = self.get_zoo(organization, zoo_name).get_model(model)
            return model_info.model_dictionary

    async def model_readme(
        self,
        organization: str,
        zoo_name: str,
        model: str,
    ) -> str:
        """Get readme file for model from the given model zoo

        - `organization`: Organization name
        - `zoo_name`: Zoo name
        - `model`: Model name
        """
        async with self._lock.reader:
            model_info = self.get_zoo(organization, zoo_name).get_model(model)
            return model_info.readme

    async def model_params(
        self,
        organization: str,
        zoo_name: str,
        model: str,
    ) -> ModelInfo:
        """Get model info for model from the given model zoo

        - `organization`: Organization name
        - `zoo_name`: Zoo name
        - `model`: Model name
        """
        async with self._lock.reader:
            return self.get_zoo(organization, zoo_name).get_model(model)

    async def download_model(
        self,
        organization: str,
        zoo_name: str,
        model: str,
    ) -> FileResponse:
        """Download model from the given model zoo

        - `organization`: Organization name
        - `zoo_name`: Zoo name
        - `model`: Model name
        """
        async with self._lock.reader:
            _ = self.get_zoo(organization, zoo_name).get_model(model)
            model_path = await self._model_path(organization, zoo_name, model)
            temp_model_path = pathlib.Path(self.temp_path()) / str(uuid4())
            await aiofiles.os.link(model_path, temp_model_path)

            async def cleanup():
                if os.path.isfile(temp_model_path):
                    await aiofiles.os.unlink(temp_model_path)

            try:
                return FileResponse(
                    temp_model_path,
                    media_type="application/octet-stream",
                    filename=model + ZooManager.model_ext,
                    background=BackgroundTask(cleanup),
                )
            except Exception:
                await cleanup()
                raise

    async def upload_model(
        self,
        *,
        organization: str,
        zoo_name: str,
        file: UploadFile,
        allow_overwrite: bool = False,
    ) -> Dict[str, str]:
        """Upload model process implementation

        - `organization`: Organization name
        - `zoo_name`: Zoo name
        - `file`: Model file to upload
        - `allow_overwrite`: Allow to overwrite model if it already exists

        Returns dictionary {"url": <model url string>}
        """

        zoo = self.get_zoo(organization, zoo_name)
        temp_model_path = pathlib.Path(self.temp_path()) / str(uuid4())
        try:
            # store input file
            await self._store_file(file, temp_model_path)

            # hard-link model file to the zoo final location
            async with self._lock.writer:
                model_name = pathlib.Path(str(file.filename)).stem
                model_path = await self._model_path(
                    organization, zoo_name, model_name, False
                )
                if os.path.isfile(model_path):
                    if not allow_overwrite:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Model {model_name} already exists in zoo {organization}/{zoo_name}",
                        )
                    else:
                        await aiofiles.os.unlink(model_path)

                await aiofiles.os.link(temp_model_path, model_path)

                model_info = await my_to_thread(
                    zoo.extract_model_info, model_path, raise_exception_on_error=True
                )
                assert model_info is not None
                zoo._models[model_name] = model_info

        finally:
            if os.path.isfile(temp_model_path):
                await aiofiles.os.unlink(temp_model_path)
        return {"url": f"{organization}/{zoo_name}/{model_name}"}

    async def delete_model(
        self, organization: str, zoo_name: str, model_name: str
    ) -> Dict[str, str]:
        """Delete model from model zoo

        - `organization`: Organization name
        - `zoo_name`: Zoo name
        - `model_name`: Model name
        """
        async with self._lock.writer:
            zoo = self.get_zoo(organization, zoo_name)
            if model_name not in zoo._models:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Model {model_name} is not found in zoo {organization}/{zoo_name}",
                )
            del zoo._models[model_name]
            model_path = await self._model_path(organization, zoo_name, model_name)
            await aiofiles.os.unlink(model_path)

            return {"url": f"{organization}/{zoo_name}/{model_name}"}

    async def _store_file(self, file_stream: UploadFile, file_path: pathlib.Path):
        """Store fastapi input file using specified path

        -`file_path`: path to store file
        -`file`: fastapi input file

        """
        try:
            archive_size = 0
            async with aiofiles.open(file_path, "wb") as f:
                while contents := await file_stream.read(0x100000):
                    archive_size += len(contents)
                    await f.write(contents)
        except Exception:
            if os.path.isfile(file_path):
                await aiofiles.os.unlink(file_path)
            raise
        finally:
            await file_stream.close()

    async def _model_path(
        self, organization: str, zoo_name: str, model: str, check_exist: bool = True
    ) -> pathlib.Path:
        """Construct full model file path from organization, zoo name, and model name"""

        assert self._zoo_root is not None
        file_path = (
            self._zoo_root / organization / zoo_name / (model + ZooManager.model_ext)
        )
        if check_exist:
            if not os.path.isfile(file_path):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Model {model} is not found in zoo {organization}/{zoo_name}",
                )
        return file_path


# Zoo manager instance
zooManager = ZooManager()


async def general_exception_handler(request: Request, e: Exception):
    """General error handling"""
    return JSONResponse(
        content=jsonable_encoder(GeneralError(detail=str(e))),
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
