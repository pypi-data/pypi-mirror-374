from pathlib import Path
from typing import Callable, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from platformdirs import user_config_dir


class Config(BaseSettings):

    # API Key
    API_KEY: Optional[str] = None
    
    # Debug mode
    DEBUG_MODE: bool = False
    DEBUG_MODE_FOLDER: str = ".debug"
    
    # Paths
    CONFIG_DIR: Path = Path(user_config_dir("synthex"))
    ANON_ID_FILE: Path = CONFIG_DIR / "anon_id.txt"
    OUTPUT_FILE_DEFAULT_NAME: Callable[[str], str] = lambda desired_format: f"synthex_output.{desired_format}"
    
    # Headers
    SYNTHEX_ANON_ID_HEADER: str = "X-Tanaos-Anon-Id"
    
    # Rate limits
    TIER_1_MAX_DATAPOINTS_PER_JOB: int = 500
    
    # Job settings
    JOB_DATA_POLLING_INTERVAL: int = 15 # interval in seconds
        
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="",
        extra="allow",
    )


config = Config() # type: ignore
