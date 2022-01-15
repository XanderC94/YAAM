'''
Requests response utility module
'''
import io
from pathlib import Path
import zipfile
import re
from urllib.parse import unquote_plus, urlparse
from requests import Response

from yaam.model.mutable.addon import Addon
from yaam.model.type.binding import BindingType

def is_zip_content(response : Response) -> bool:
    '''
    Check if the response is referring to a compressed archive (.zip)
    '''

    return (
        response.url.endswith(".zip") or
        ('Content-Disposition' in response.headers and response.headers['Content-Disposition'].endswith(".zip"))
    )

def is_json_content(response : Response) -> bool:
    '''
    Check if the response is referring to a JSON object file (.json)
    '''

    return (
        response.url.endswith(".json") or
        ('Content-Type' in response.headers and 'application/json' in response.headers['Content-Type'])
    )

def get_filename(response: Response) -> str:
    '''
    Return the name of the file from the respose, if exists
    '''
    name = None

    content_disp = response.headers.get('content-disposition', None)
    if content_disp is not None:
        matches = re.findall(r"filename=\"?(.+)\"?", content_disp)
        if len(matches) > 0:
            name = matches[0]

    if name is None:
        decoded_url = unquote_plus(response.url)
        parsed_url = urlparse(decoded_url)

        url_path = Path(parsed_url.path)

        if len(url_path.suffix) > 0 and url_path.suffix != '.':
            name = url_path.name

    return name

def find_filename(response: Response, target : str) -> bool:
    '''
    Return true if the response contains the target filename
    '''
    found = False

    content_disp = response.headers.get('content-disposition', None)

    escaped_target = target.replace('.', '\\.')

    if content_disp is not None:
        matches = re.findall(content_disp, f"filename=\"?({escaped_target})\"?")
        found = len(matches) > 0

    if not found:
        decoded_url = unquote_plus(response.url)
        parsed_url = urlparse(decoded_url)
        url_path = Path(parsed_url.path)
        found = url_path.name == target

    return found

def unpack_content(response : Response, addon: Addon) -> bytes:
    '''
    Unpack response datastream
    '''

    data : bytes = response.content

    lookup_suffix = addon.binding.typing.suffix
    if addon.binding.typing == BindingType.AGNOSTIC:
        lookup_suffix = addon.binding.path.suffix

    if is_zip_content(response):
        file_like_object = io.BytesIO(data)
        zip_data = zipfile.ZipFile(file_like_object)

        for entry in zip_data.filelist:
            if entry.filename.endswith(lookup_suffix):
                handle = zip_data.open(entry.filename)
                data = handle.read()
                handle.close()
                break

    return data

def repack_to_zip(content : bytes) -> zipfile.ZipFile:
    '''
    unpack content bytes to a zip
    '''

    file_like_object = io.BytesIO(content)
    zip_data = zipfile.ZipFile(file_like_object)

    return zip_data
