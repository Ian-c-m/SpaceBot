import random, logging
from enum import Enum
log = logging.getLogger(__name__)

class Planet(str, Enum):
    Sun = "sun"
    Mercury = "mercury"
    Venus = "venus"
    Earth = "earth"
    Mars = "mars"
    Jupiter = "jupiter"
    Saturn = "saturn"
    Uranus = "uranus"
    Neptune = "neptune"
    Pluto = "pluto"
    

planet_weather = {
    "mercury": "Mercury averages 800°F (430°C) during the day, -290°F (-180°C) at night.\n       Quite windy, so make sure to grab a jacket before heading out.",
    "venus": "Venus averages 880°F (471°C).\n        Acid rain likely, so bring an umbrella.",
    "earth": "Earth averages 61°F (16°C).\n      There will be weather.",
    "mars": "Mars averages -20°F (-28°C).\n      A little chilly out, so don't forget a jumper.",
    "jupiter": "Jupiter averages -162°F (-108°C).\n      There's no solid ground, you'll need a yacht.",
    "saturn": "Saturn averages -218°F (-138°C).\n      Big storms at the north pole, and watch out for the strong winds.",
    "uranus": "Uranus averages -320°F (-195°C).\n      A little nippy, so wrap up well.",
    "neptune": "Neptune averages -331°F (-201°C).\n      Winds are picking up, so be careful out there!",
    "pluto": "Pluto averages -388°F (-233°C).\n      I'm still annoyed that it's not a planet.",
    "sun": "The sun is basically a spicy planet.\n      It's very warm. Wear sunscreen."
    }


def get_planet_weather(planet: str = None):

    """Gives the weather of a planet.
   
    Parameters
    ----------
    planet: :class:`Planet`
        A planet from our solar system. Can be omitted to return a random planet instead.

    Returns
    ----------
        weather_return: :class:`str` | :class:`int`
            The weather of the given planet. 0 if there is an error.
        error_message: :class:`str` | :class:`int`
            The error message if there is one. 0 if there is not an error.
    """


    try:
        if planet is None:
            #no planet was given, so return a random planet's weather instead.
            weather_return = str(random.choice(list(planet_weather.values())))
        
        else:
            #return the weather of the given planet.
            weather_return = str(planet_weather[planet])

        #successfully got a planet's weather, so no error message to return
        log.debug(f"module_weather - get_planet_weather - weather was found")
        return (weather_return, 0)



    except Exception as e:        
        error_message = f"Failed to get_planet_weather. {e}"
        log.exception(f"module_weather - get_planet_weather - Failed to get_planet_weather. {e}.")

        #failed to get a planet's weather, so nothing to return for that.
        return (0, error_message)
    
