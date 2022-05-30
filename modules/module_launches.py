import requests, disnake, logging
from modules.module_config import launch_url
from datetime import datetime
log = logging.getLogger(__name__)
#launch_url = "https://fdo.rocketlaunch.live/json/launches/next/5"

def get_basic_launch_info():

    """Returns basic information about the next 5 scheduled launches.
   
    Parameters
    ----------
    None

    returns
    ----------
        launch_embed: :class:`disnake.Embed`  | :class:`int`
            An embed object with info of the launches. 0 if there was an error.
        error_message: :class:`str` | :class:`int`
            The error/exception message if there is one. 0 if there was no error.
    """


    response = requests.get(launch_url)
    response_json = response.json()
    
    launch_embed = disnake.Embed(title="Next 5 scheduled rocket launches")
    
    for i in range(5):
        #loop through the 5 launches and add them to the embed
        try:
            launch = response_json["result"][i]

            launch_description = launch["launch_description"]            
            launch_mission = launch["name"]

            launch_embed.add_field(name=launch_mission, value=launch_description, inline = False)


        except Exception as e:
            error_message = f"Failed to add item to embed. {e}"
            log.exception(f"module_launches - get_basic_launch_info - Failed to add item to embed. {e}")
            return 0, error_message


    launch_embed.set_footer(text="Data by RocketLaunch.Live")
    return launch_embed, 0



def get_detailed_launch_info(launch_mission: str):

    """Returns detailed information about the given launch.
   
    Parameters
    ----------
    launch_mission: :class:`str`
        The name of the launch. Same as the "launch_mission" from the get_basic_launch_info()

    returns
    ----------
        launch_embed: :class:`disnake.Embed`  | :class:`int`
            An embed object with info of the launches. 0 if there was an error.
        error_message: :class:`str` | :class:`int`
            The error/exception message if there is one. 0 if there was no error.
    """

    response = requests.get(launch_url)
    response_json = response.json()
    launch = ""
    try:

        for i in range(5):
            #loop through the missions and find one that matches the given mission
            if response_json["result"][i]["name"] == launch_mission:
                launch = response_json["result"][i]
                break

        if launch == "":
            #if we couldn't find the given launch then raise a value error to log it.
            log.exception("module_launches - get_detailed_launch_info - launch was empty")
            raise ValueError("launch was empty")


    except ValueError as e:
        #for when the launch couldn't be found.
        error_message = f"Couldn't find the given mission {launch_mission}. {e}"
        log.exception(f"module_launches - get_detailed_launch_info - Couldn't find the given mission {launch_mission}. {e}")
        return 0, error_message   


    except Exception as e:
        #generic catch all exception.
        error_message = e
        log.exception(f"module_launches - get_detailed_launch_info - {e}.")
        return 0, error_message    

    try:
        #assemble the embed object to return the information back.
        launch_provider = launch["provider"]["name"]
        launch_vehicle = launch["vehicle"]["name"]

        launch_pad_name = launch["pad"]["name"]
        launch_pad_location = launch["pad"]["location"]["name"]
        launch_pad_country = launch["pad"]["location"]["country"]
        full_location = f"{launch_pad_name}, {launch_pad_location}, {launch_pad_country}."

        launch_date = int(launch["sort_date"])
        launch_date = datetime.utcfromtimestamp(launch_date).strftime('%Y-%m-%d %H:%M:%S')


        launch_embed = disnake.Embed(title=f"Information about {launch_mission}")
        launch_embed.add_field(name="Launch Date",value=launch_date,inline=False)
        launch_embed.add_field(name="Provider", value=launch_provider, inline=True)    
        launch_embed.add_field(name="Vehicle",value=launch_vehicle,inline=True)
        launch_embed.add_field(name="Location",value=full_location,inline=False)
        launch_embed.set_footer(text="Data by RocketLaunch.Live")

        log.debug(f"module_launches - get_detailed_launch_info - {launch_vehicle} found successfully.")
        return launch_embed, 0

    except Exception as e:
            #if we failed to assemble the embed
            error_message = e
            log.exception(f"module_launches - get_detailed_launch_info - {e}")
            return 0, error_message  