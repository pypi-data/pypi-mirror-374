import dataclasses
from ..core import File as File

@dataclasses.dataclass
class AutodeskFileVersion:
    """ ::version(v14.25.0)

    .. warning:: Do not instantiate this class directly, it is created from :class:`AutodeskFile`.

    """
    @property
    def urn(self) -> str:
        ''' Get the unique resource name (also called "id") of this version of the file on Autodesk cloud storage. '''
    @property
    def attributes(self) -> dict:
        """ Get the attributes of the latest version of the file on Autodesk cloud storage. """
    def get_file(self) -> File:
        """ Download the content of the latest version of the file from Autodesk cloud storage. """
    def __init__(self, _access_token, _data) -> None: ...

class AutodeskFile:
    """ ::version(v14.25.0)

    Represents a file stored on Autodesk cloud storage (https://aps.autodesk.com/data-management-api)
    """
    def __init__(self, url: str) -> None: ...
    @property
    def url(self) -> str:
        """ URL of the file on Autodesk cloud storage. """
    def get_latest_version(self, access_token: str) -> AutodeskFileVersion:
        """ Get the latest version of the file on Autodesk cloud storage.

        :param access_token: Autodesk cloud storage token to access the file.
        """
