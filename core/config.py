from typing import Any, Dict, List, Optional, TypeVar, Generic
from pydantic_settings import BaseSettings

from pydantic import AnyHttpUrl, validator,BaseModel
from fastapi import Query
from fastapi_pagination.default import Page as BasePage, Params as BaseParams
from datetime import datetime
import warnings


warnings.filterwarnings("ignore", message="Valid config keys have changed in V2")
warnings.filterwarnings("ignore", message="Field .* has conflict with protected namespace .*")


T = TypeVar("T")

class Params(BaseParams):
    size: int = Query(500, gt=0, le=1000, description="Page size")

class Page(BasePage[T], Generic[T]):
    __params_type__ = Params


base_domain = "http://192.168.4.230/"
base_url ="http://192.168.4.230"
device_base_url = "http://cbe.themaestro.in:8023/device_api"
base_dir=""
base_domain_url = ""
base_url_segment = "/bull-api"    
base_upload_folder = "/var/www/html"
data_base = "mysql+pymysql://python_admin:12345@192.168.1.108/bull_db"
device_code = "MAE238"

#3BDPn79Ss4DLS38Gy2FIriANyxf5sWnTew20drhkl
 
api_doc_path = "/docs"

class Settings(BaseSettings):
    API_V1_STR: str = base_url_segment
    BASE_UPLOAD_FOLDER: str = base_upload_folder
    DEVICE_BASE_URL: str = device_base_url
    BASEURL:str=base_url
    BASE_DIR:str=base_dir
    SALT_KEY:str="L4jkmn71iwelcv@1qaz!"
    DEVICE_SALT_KEY:str="DeviceTnr34230920Bullqwer" 
    DEFAULT_KEY:str="indiaTnR2020bullmconnecta1287542"
    SECRET_KEY:str=""
    DATA_BASE:str = data_base
    BASE_DOMAIN:str = base_domain
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    BASE_DOMAIN_URL:str = base_domain_url
    API_DOC_PATH:str = api_doc_path
    otp_resend_remaining_sec:int = 120
    DEVICE_CODE : str = device_code
  
    SERVER_NAME:str = "BULL Application"
    ROOT_SERVER_BASE_URL:str =""
    SERVER_HOST:AnyHttpUrl="http://localhost:8000"
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = ["http://localhost:8000","http://localhost:8002",  "http://localhost:8080", "http://localhost:3000",
                                              "http://localhost:3001", "http://localhost:3002", "https://cbe.themaestro.in", "http://cbe.themaestro.in",
                                              ]       
    
    PROJECT_NAME:str = "BULL Application"

    SQLALCHEMY_DATABASE_URI: Optional[str] = None

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v

        return data_base

settings = Settings()


