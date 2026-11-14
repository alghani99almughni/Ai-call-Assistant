from pydantic_settings import BaseSettings,SettingsConfigDict
class Settings(BaseSettings):
 model_config=SettingsConfigDict(env_file=".env",extra="ignore")
 database_url:str="postgresql+asyncpg://voice:change-me@localhost:5432/voice";redis_url:str="redis://localhost:6379/0"
 ollama_url:str="http://localhost:11434";ollama_model:str="qwen2.5:7b";whisper_model:str="small";app_secret:str="unsafe-development-secret"
 public_base_url:str="https://example.invalid"
 voicelink_api_url:str="https://api.voicelink.co.in";voicelink_api_key:str="";voicelink_sip_domain:str="sip.voicelink.co.in"
