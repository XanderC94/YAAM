'''
Requests response utility module
'''
import io
import zipfile
from requests import Response

from yaam.model.mutable.addon import Addon
from yaam.model.type.binding import BindingType

def is_zip_content(response : Response) -> bool:
    '''
    Check if the response is referring to a compressed archive (.zip) 
    '''

    return (
        ('Content-Type' in response.headers and 'application/json' in response.headers['Content-Type']) or
        ('Content-Disposition' in response.headers and response.headers['Content-Disposition'].endswith(".zip"))
    )

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

def unpack_zip(content : bytes) -> zipfile.ZipFile:
    '''
    unpack content bytes to a zip
    '''

    file_like_object = io.BytesIO(content)
    zip_data = zipfile.ZipFile(file_like_object)
    
    return zip_data
