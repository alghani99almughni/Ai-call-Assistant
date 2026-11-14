from pydantic_settings import BaseSettings, SettingsConfigDict
class Settings(BaseSettings):
    model_config=SettingsConfigDict(env_file=".env",extra="ignore")
    database_url:str="postgresql+asyncpg://voice:change-me@localhost:5432/voice"
    redis_url:str="redis://localhost:6379/0"
    ollama_url:str="http://localhost:11434"
    ollama_model:str="qwen2.5:7b"
    whisper_model:str="small"
    app_secret:str="unsafe-development-secret"
    # Twilio: set PUBLIC_BASE_URL to HTTPS reachable by Twilio (ngrok for local dev).
    public_base_url:str="https://example.invalid"
    twilio_auth_token:str=""
    twilio_validate_signature:bool=True
    twilio_voice:str="Polly.Joanna"
    twilio_language:str="en-US"
