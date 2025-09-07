import traceback

from .avatar_component import IAvatarComponent
from pathlib import Path
import os
import flask
import io
from foundation_kaia.marshalling import ApiUtils
import requests
import uuid

class FileCacheComponent(IAvatarComponent):
    def __init__(self, folder: Path):
        self.folder = folder

    def setup_server(self, app: IAvatarComponent.App, address: str):
        os.makedirs(self.folder, exist_ok=True)
        app.add_url_rule('/file-cache/upload/<file_name>', view_func=self.file_cache_upload, methods=['POST'])
        app.add_url_rule('/file-cache/download/<file_name>', view_func=self.file_cache_download, methods=['GET'])
        app.add_url_rule('/file-cache/list', view_func=self.file_cache_list, methods=['GET'])
        app.add_url_rule('/file-cache/delete/<file_name>', view_func=self.file_cache_delete, methods=['POST'])



    def file_cache_upload(self, file_name: str):
        with open(self.folder/file_name, 'wb') as file:
            uploaded_file = flask.request.files['content']  # Use the field name from the client
            file.write(uploaded_file.read())
        return 'OK'

    def file_cache_download(self, file_name: str):
        with open(self.folder / file_name, 'rb') as file:
            return flask.send_file(
                io.BytesIO(file.read()),
                mimetype='application/octet-stream'
            )

    def file_cache_delete(self, file_name: str):
        os.unlink(self.folder/file_name)
        return 'OK'

    def file_cache_list(self):
        suffix = flask.request.args.get('suffix',None)
        prefix = flask.request.args.get('prefix',None)
        result = []
        for f in os.listdir(self.folder):
            if prefix is not None and not f.startswith(prefix):
                continue
            if suffix is not None and not f.endswith(suffix):
                continue
            result.append(f)
        return flask.jsonify(result)



class FileCacheApi:
    def __init__(self, address: str):
        ApiUtils.check_address(address)
        self.address = address

    def download(self, file_name: str) -> bytes:
        response = requests.get(f'http://{self.address}/file-cache/download/{file_name}')
        if response.status_code!=200:
            raise ValueError(response.text)
        return response.content

    def upload(self, content: bytes, file_name: str|None = None):
        if file_name is None:
            file_name = str(uuid.uuid4())
        response = requests.post(
            f'http://{self.address}/file-cache/upload/{file_name}',
            files=(
                      ('content', content),
                  )
        )
        if response.status_code!=200:
            raise ValueError(response.text)
        return file_name



    def list(self, prefix: str | None = None, suffix: str | None = None) -> list[str]:
        params = {}
        if prefix is not None:
            params["prefix"] = prefix
        if suffix is not None:
            params["suffix"] = suffix
        resp = requests.get(f"http://{self.address}/file-cache/list", params=params)
        if resp.status_code!=200:
            raise ValueError(resp.text)
        return resp.json()

    def delete(self, file_name: str):
        resp = requests.post(f"http://{self.address}/file-cache/delete/{file_name}")
        if resp.status_code != 200:
            raise ValueError(resp.text)
