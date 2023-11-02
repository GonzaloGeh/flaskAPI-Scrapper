from pydantic import BaseModel

class SearchParametersModel(BaseModel):
    baseUrl: str
    firstName: str | None = None
    lastName: str
    county: str
    yob: str
    # ADD MORE PARAMETERS AS NEEDED