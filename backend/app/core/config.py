from pathlib import Path


class Settings:
    BASE_DIR = Path(__file__).parent.parent.parent
    UPLOAD_DIR = BASE_DIR / 'uploads'
    STATIC_DIR = BASE_DIR / 'static'
    WORKSPACE_DIR = BASE_DIR / 'workspace'
    FONTS_DIR = BASE_DIR / 'fonts'
    YAHEI_CONSOLAS_FONT_PATH = FONTS_DIR / 'YaHei Consolas Hybrid 1.12.ttf'


settings = Settings()


def init():
    for dir in [
        settings.UPLOAD_DIR,
        settings.STATIC_DIR,
        settings.WORKSPACE_DIR
    ]:
        if not dir.exists():
            dir.mkdir(parents=True, exist_ok=True)


init()
