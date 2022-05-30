from enum import Enum
import requests, json, datetime, urllib, os, logging
from modules.module_config import apod_url, mars_url
from tokens import nasa_api_key

log = logging.getLogger(__name__)


class Location(str, Enum):
    Mars = "mars"
    space = "apod"



def get_apod():
    """Creates metadata for NASA's Astrology Picture Of the Day.

    Parameters
    ----------
    None

    returns
    ----------
        error_message: :class:`str` | :class:`int`
            The error/exception message if there is one. 0 if there was no error.
    """

    try:
          
        error_message = ""
        last_run = ""

        #check the last time we got the photo. 
        with open("apod_data.txt", "r") as json_file:
            try:
                metadata = json.load(json_file)
                for data in metadata:                
                    last_run = data['last_run']   

            #if file is empty, then set a default value
            except json.JSONDecodeError:                
                last_run = None
                pass


    #if the file doesn't exist, then create it.
    except IOError:
        with open("apod_data.txt", "w") as json_file:
            log.debug("module_photos - get_apod - Created new apod_data.txt file")
            json_file.close()
        pass
        

                
    date_today = datetime.datetime.today().strftime('%Y-%m-%d')
    
    #need to fetch new apod if it hasn't been done today, or we don't know when it was last done.      
    if last_run != date_today or last_run is None:
        log.debug("module_photos - get_apod - module_photos - last_run was none.")        
        last_run = date_today            
        

        with urllib.request.urlopen(apod_url) as url:
            data = json.loads(url.read().decode())

            #checking remaining API limits
            headers = url.headers
            hourly_limit_remaining = int(headers['X-RateLimit-Remaining'])                
            if hourly_limit_remaining <= 100:
                error_message = f"Only {hourly_limit_remaining}/1000 requests left this hour."
                log.warning(f"module_photos - get_apod - Only {hourly_limit_remaining}/1000 requests left this hour.")
                
                #TODO: actually do something if we reach this limit.


            #check that we actually got a response from the API
            if data is not None:
                #check if media is a video
                if data['media_type'] == "video":
                    vid_url = data['url']
                    vid_title = data['title']
                    vid_explanation = data['explanation']
                    

                    #saving metadata to file to reference later. saves API calls as only checking once a day for new pic.
                    apod_data = [{'last_run':last_run, 'media_type':'video', 'url':vid_url, 'title':vid_title, 'explanation':vid_explanation}]

                    with open ("apod_data.txt", "w") as outfile:
                        json.dump(apod_data, outfile)

                    #succeeded so no error message.                        
                    return 0 

                
                #media is an image
                elif data['media_type'] == "image":
                    
                    #get info of the image
                    pic_url = data['hdurl']                        
                    pic_title = data['title']
                    pic_explanation = data['explanation']
                    
                    #save image url as a generic url
                    response = requests.get(pic_url)
                    extension = os.path.splitext(pic_url)[1][1:]
                    apod_file = "apod." + extension
                    
                    #saving image to file
                    file = open(apod_file, "wb")
                    file.write(response.content)
                    file.close()
                    
                    #saving metadata to file to reference later. saves API calls as only checking once a day for new pic.
                    apod_data = [{'last_run':last_run, 'media_type':'image', 'url':pic_url, 'title':pic_title, 'explanation':pic_explanation, 'file_type':extension}]

                    with open ("apod_data.txt", "w") as outfile:
                        json.dump(apod_data, outfile)

                    #succeeded so no error message.  
                    return 0

                else:
                    #the media we got was not an image or a video.
                    error_message += f"APOD was not an image or video, instead was {data['media_type']}"
                    log.warning(f"module_photos - get_apod - APOD was not an image or video, instead was {data['media_type']}")
                    return error_message

                
            else:
                #data is None
                error_message += "Failed to get APOD, no data from API."
                log.warning("module_photos - get_apod - Failed to get APOD, no data from API.")
                return error_message

        
    else:            
        #no need to get a new image as we've already checked it today.
        return 0



def get_mars():
    """Creates metadata for NASA's latest Curiosity rover photos.

    Parameters
    ----------
    None

    returns
    ----------
    error_message: :class:`str`
        The error message (if any).

    front_photo_link: :class:`str`
        The url for the latest front camera photo.

    rear_photo_link: :class:`str`
        The url for the latest rear camera photo.

    nav_photo_link: :class:`str`
        The url for the latest nav camera photo.

    photo_date: :class:`str`
        The date of the photos
    """

    error_message = ""
    needed_cameras = ["FHAZ", "RHAZ", "NAVCAM"]

    with urllib.request.urlopen(mars_url) as url:   

        #checking remaining API limits
        headers = url.headers
        hourly_limit_remaining = int(headers['X-RateLimit-Remaining'])
                
        if hourly_limit_remaining <= 100 and hourly_limit_remaining >0 :
            log.warning(f"module_photos - get_mars - Only {hourly_limit_remaining}/1000 requests left this hour.")
            print(f"WARNING module_photos - get_mars - Only {hourly_limit_remaining}/1000 requests left this hour.")

        elif hourly_limit_remaining <= 0:
            #we used all our api calls up
            log.warning(f"module_photos - get_mars - No requests left this hour")
            print("WARNING module_photos - get_mars - No requests left this hour.")
            error_message += "module_photos - get_mars - No requests left this hour"
            return error_message, None, None, None, None
                
        data = json.loads(url.read().decode())

        if data is not None: #check that we actually got data back
            log.debug("module_photos - get_mars - Manifest data retrieved successfully")    

            #get the date of the last photo to use when getting the photo url
            max_sol = data['photo_manifest']['max_sol']
            
            #find the last entry in the manifest of photos
            last_entry = data['photo_manifest']['photos'][-1]

            log.debug(f"module_photos - get_mars - available cameras are: {last_entry['cameras']}")

            for cam in needed_cameras:
                if cam not in last_entry['cameras']:
                #if the last day doesn't have all entries, then only return the photos for the ones that do appear
                    log.warning(f"module_photos - get_mars - {cam} not in cameras")
                    
                        
        else:
            log.warning("module_photos - get_mars - No data returned from mars_url")
            error_message += "module_photos - get_mars - No data returned from mars_url"
            return error_message, None, None, None, None


    #get three photos (if possible) from front, rear and nav cameras
       
    fhaz_photo = f"https://api.nasa.gov/mars-photos/api/v1/rovers/Curiosity/photos?camera=FHAZ&sol={max_sol}&api_key={nasa_api_key}"
    rhaz_photo = f"https://api.nasa.gov/mars-photos/api/v1/rovers/Curiosity/photos?camera=RHAZ&sol={max_sol}&api_key={nasa_api_key}"
    nav_photo = f"https://api.nasa.gov/mars-photos/api/v1/rovers/Curiosity/photos?camera=NAVCAM&sol={max_sol}&api_key={nasa_api_key}"

    photo_date = ""

    with urllib.request.urlopen(fhaz_photo) as fhaz:
        front_data = json.loads(fhaz.read().decode())       

        if len(front_data["photos"]) > 0:            
            front_photo_link = front_data['photos'][-1]['img_src']
            photo_date = front_data['photos'][-1]['earth_date']
                
        else:
            front_photo_link = None            
            error_message += "No front_photo_link. "
            log.warning("module_photos - get_mars - No front_photo_link.")


    with urllib.request.urlopen(rhaz_photo) as rhaz:
        rear_data = json.loads(rhaz.read().decode())

        if len(rear_data["photos"]) > 0:            
            rear_photo_link = rear_data['photos'][-1]['img_src']

        else:
            rear_photo_link = None
            error_message += "No rear_photo_link. "
            log.warning("module_photos - get_mars - No rear_photo_link.")
    

    with urllib.request.urlopen(nav_photo) as nav:
        nav_data = json.loads(nav.read().decode())

        if len(nav_data["photos"]) > 0:            
            nav_photo_link = nav_data['photos'][-1]['img_src']

        else:
            nav_photo_link = None
            error_message += "No nav_photo_link."
            log.warning("module_photos - get_mars - No nav_photo_link.")
    

    return error_message, front_photo_link, rear_photo_link, nav_photo_link, photo_date
