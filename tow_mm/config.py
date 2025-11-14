import dataclasses


@dataclasses.dataclass
class Config:
    app_url: str
    uploads_url: str