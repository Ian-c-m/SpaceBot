import tokens
#for module_news
news_url = "https://www.space.com/feeds/all"

#for module_iss
iss_url = "http://api.open-notify.org/iss-now.json"

#for module_launches
launch_url = "https://fdo.rocketlaunch.live/json/launches/next/5"



#for module_astro
astro_url = "http://api.open-notify.org/astros.json"

#for module_photos
apod_url = f"https://api.nasa.gov/planetary/apod?api_key={tokens.nasa_api_key}"
mars_url = f"https://api.nasa.gov/mars-photos/api/v1/manifests/Curiosity?api_key={tokens.nasa_api_key}"