from pydantic import BaseModel, StrictBool, StrictInt, StrictStr, model_validator


class RunRequest(BaseModel):
    "The parameters of a 'run' request to a Container tool"

    tool_id: StrictStr
    container: StrictStr
    command: list[StrictStr]
    username: StrictStr | None = None
    password: StrictStr | None = None

    @model_validator(mode="after")
    def check_both_credentials_or_neither(self) -> "RunRequest":
        """Ensure that either both username and password or set, or neither are set"""
        assert (self.username is None and self.password is None) or (
            self.username is not None and self.password is not None
        )
        return self


class SignalRequest(BaseModel):
    """The parameters of a 'signal' request to a Container tool"""

    tool_id: StrictStr
    signal: StrictStr


class GetStdoutResponse(BaseModel):
    """The response of a 'get_stdout' request to a Container tool"""

    stdout: StrictStr


class GetStateResponse(BaseModel):
    """The response of a 'get_state' request to a Container tool"""

    running: StrictBool
    return_code: StrictInt | None = None


class GetStderrResponse(BaseModel):
    """The response of a 'get_stderr request to a Container tool"""

    stderr: StrictStr
