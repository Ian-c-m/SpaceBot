import requests, logging
from modules.module_config import iss_url

log = logging.getLogger(__name__)

def get_iss():

    """Returns the location of the ISS.
   
    Parameters
    ----------
    None

    returns
    ----------
        iss_loc: :class:`list`  | :class:`int`
            A list of latitude and longitude (lat, lon). 0 if there was an error.
        error_message: :class:`str` | :class:`int`
            The error/exception message if there is one. 0 if there was no error.
    """

    try:
        
        r = requests.get(iss_url)    
        x = r.json()
        lat = x["iss_position"]["latitude"]
        lon = x["iss_position"]["longitude"]
        iss_loc = [lat, lon]
        return (iss_loc, 0)
    

    except Exception as e:
        error_message = (f"Failed to get_iss. {e}.")
        log.exception = (f"module_iss - get_iss - Failed to find iss. {e}.")
        return (0, error_message)