from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "My League Oracle"
    current_season: int = 2024
    teams_2022: list = [
        "548",
        "728",
        "541",
        "546",
        "723",
        "547",
        "727",
        "533",
        "530",
        "543",
        "536",
        "797",
        "724",
        "720",
        "529",
        "532",
        "798",
        "540",
        "538",
        "531",
    ]
    teams_2023: list = [
        "548",
        "541",
        "715",
        "546",
        "723",
        "534",
        "547",
        "727",
        "533",
        "530",
        "543",
        "536",
        "542",
        "724",
        "529",
        "532",
        "538",
        "531",
    ]
    teams_2024: list = [
        "548",
        "541",
        "728",
        "546",
        "534",
        "547",
        "727",
        "530",
        "533",
        "543",
        "536",
        "542",
        "720",
        "529",
        "537",
        "798",
        "532",
        "540",
        "531",
        "538",
    ]


settings = Settings()
