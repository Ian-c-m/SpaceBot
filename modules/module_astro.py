import requests, disnake, logging
from modules.module_config import astro_url

log = logging.getLogger(__name__)

def get_astros():
    """Returns the people in space.

    Parameters
    ----------
    None

    returns
    ----------
        astros: :class:`str` | :class:`int`
            An formatted string of people in space listed by craft. 0 if there was an error.
        error_message: :class:`str` | :class:`int`
            The error/exception message if there is one. 0 if there was no error.
    """

    astro_request = requests.get(astro_url)  
    astro_request = astro_request.json()
    astro_count = astro_request["number"]

    try:
        if astro_request["message"] == "success":

            crafts = set(())
            astro_message = f"\n**There are {astro_count} people in space right now!** \n\n"

            for person in astro_request["people"]:
                #get a set of all crafts.
                crafts.add(person["craft"])

            for craft in crafts:
                #loop through crafts and assemble message with people in it
                astro_message += f"__{craft}__ \n"

                for person in astro_request["people"]:
                    #find all the people on board the craft and add them to the message
                    if person["craft"] == craft:
                        astro_message += f"· {person['name']} \n"

            
            return astro_message, 0


        else:
            #raise AttributeError("Failed to get Astros data from API.")
            log.warning("module_astro - get_astro - Failed to get Astros data from API.")


    except Exception as e:       
        log.exception(f"module_astro - get_astro - {e}.")
        return 0, e
