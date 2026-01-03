from pydantic import Field

from app.configs.packaging.pyproject import PyProjectTomlConfig

class PackagingInfo(PyProjectTomlConfig):
    COMMIT_SHA: str = Field(
        description="SHA-1 checksum of the git commit used to build the app",
        default="",
    )