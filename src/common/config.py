from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv(override=True)


class GlobalSettings(BaseSettings):
    GOOGLE_API_KEY: str = Field(
        default='',
        description='Gemini API key for Google services.',
    )
    OPENAI_API_KEY: str = Field(
        default='',
        description='OpenAI API key for OpenAI services.',
    )
    LANGSMITH_API_KEY: str = Field(
        default='',
        description='LangSmith API key for LangSmith services.',
    )
    LANGSMITH_TRACING: bool = Field(
        default=False,
        description='Enable or disable LangSmith tracing.',
    )
    LANGSMITH_ENDPOINT: str = Field(
        default='https://api.smith.langchain.com',
        description='LangSmith API endpoint.',
    )
    LANGSMITH_PROJECT: str = Field(
        default='',
        description='LangSmith project name for LangSmith services.',
    )
    TAVILY_API_KEY: str = Field(
        default='',
        description='Tavily API key for Tavily services.',
    )
    model_config = SettingsConfigDict(
        env_file='.env',
    )


class Settings(GlobalSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
    )


settings = Settings()
