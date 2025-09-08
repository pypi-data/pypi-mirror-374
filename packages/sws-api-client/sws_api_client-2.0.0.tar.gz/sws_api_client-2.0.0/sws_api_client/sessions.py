import datetime
from typing import Optional

from pydantic import BaseModel
from sws_api_client.datasets import Datasets
from sws_api_client.sws_api_client import SwsApiClient

import logging

logger = logging.getLogger(__name__)

class SessionListItemModel(BaseModel):

    """Model representing a session list item.
    Attributes:
        description (str): Description of the session
        id (int): Unique identifier of the session
        creationDate (int): Creation date of the session in milliseconds since epoch
        updateDate (int): Update date of the session in milliseconds since epoch
        dataSetCode (str): Code of the dataset associated with the session
        dataSetName (str): Name of the dataset associated with the session
        domainCode (str): Code of the domain associated with the session
        domainName (str): Name of the domain associated with the session
        userName (str): Name of the user who created or updated the session
        userEmail (Optional[str]): Email of the user who created or updated the session
        dirty (bool): Indicates if the session is dirty
        willConflict (bool): Indicates if there will be a conflict with this session
    """
    description: str
    id: int
    creationDate: int
    updateDate: int
    dataSetCode: str
    dataSetName: str
    domainCode: str
    domainName: str
    userName: str
    userEmail: Optional[str]
    dirty: bool
    willConflict: bool

class SessionExtendedItemModel(BaseModel):

    """Model representing an extended session item.
    Attributes:
        session (SessionListItemModel): Basic session information
        dimensions (List[dict]): List of dimensions associated with the session
        flags (List[dict]): List of flags associated with the session
        pivoting (dict): Pivoting information for the session
    """
    session: dict
    dimensions: list[dict]
    flags: list[dict]
    pivoting: dict

    

class Sessions:
    """Class for managing sessions operations through the SWS API.

    This class provides methods for creating, updating, and deleting sessions

    Args:
        sws_client (SwsApiClient): An instance of the SWS API client
    """

    def __init__(self, sws_client: SwsApiClient) -> None:
        """Initialize the Datasets manager with SWS client."""
        self.sws_client = sws_client
        self.datasets = Datasets(sws_client)
    
    def get_all_sessions(self) -> dict:
        """Get all sessions.

        Returns:
            dict: Dictionary containing all sessions
        """
        url = f"/session"

        response = self.sws_client.discoverable.get('is_api', url, )
        # map response to an array of SessionListItemModel
        return [SessionListItemModel(**item) for item in response]
    
    def get_session(self, session_id: int) -> dict:
        """Get a session by its ID.

        Args:
            session_id (int): The identifier of the session

        Returns:
            dict: The requested session
        """
        url = f"/session/{session_id}"

        response = self.sws_client.discoverable.get('session_api', url)
        return SessionExtendedItemModel(**response)
    
    def create_session(self, dataset_id:str, dimensions:dict, name:str = None) -> SessionExtendedItemModel: 
        """Create a new session.

        Args:
            dataset (str): The identifier of the dataset
            dimensions (dict): The dimensions of the session
        """
        # convert dimenisons codes to internal ids
        dataset = self.datasets.get_dataset_info(dataset_id)
        ids = self.datasets.convert_codes_to_ids(dataset, codes=dimensions)
        # {"domainCode":"agriculture","dataSetCode":"aproduction","dimension2ids":{"geographicAreaM49":[144],"measuredElement":[216],"measuredItemCPC":[3],"timePointYears":[112]},"sessionDescription":"AGR 2025-04-14 09:38:11"}

        # create a session name as a first three letters of the dataset capitalized id plus the current date
        # and time in the format YYYY-MM-DD HH:MM:SS
        new_session_name = f"{dataset_id[:3].upper()} {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

        url = f"/session"
        data = {
            "domainCode": dataset.dataset.domain.id,
            "dataSetCode": dataset.dataset.id,
            "dimension2ids": ids,
            "sessionDescription": name if name is not None else new_session_name
        }
        response = self.sws_client.discoverable.post('is_api', url, data=data)
        new_id = response.get('result').get('id')
        return new_id
            
    def delete_sessions(self, ids:list[str]) -> None:
        """Delete one or more sessions.

        Args:
            ids (list[str]): The identifiers of the sessions
        """
        url = f"/session"
        data = {
            "ids": ids
        }
        result = self.sws_client.discoverable.delete('is_api', url, data=data)
        if result.get('success'):
            return True
        else:
            # log the error
            logger.error(f"Error deleting sessions: {result.get('error')}")
            return False
    

        

