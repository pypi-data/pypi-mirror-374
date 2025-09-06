from agora_logging import logger
from agora_config import config
from .curl_wrapper import CurlWrapper
import json
class GPSSingleton: 
    _instance = None
    _site_url = "http://172.17.0.1:5000/gps/info/"
    _header = { "accept", "application/json" }
    _curl_Wrapper = None
        
    def __init__(self) -> None:
        super().__init__()
        self._curl_Wrapper = CurlWrapper()
        gps_url = config["AEA2:GpsUrl"]
        if gps_url is not None and gps_url !="":
            self._site_url = gps_url
 
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance     
    
    def get_gps_info(self):
        try:
            response = self._curl_Wrapper.get_response(self._site_url, self._header)      
            return json.dumps(response)
        except Exception as error:
            logger.exception(error, "Exception occured while gps info...")
            return None
            
Gps = GPSSingleton()