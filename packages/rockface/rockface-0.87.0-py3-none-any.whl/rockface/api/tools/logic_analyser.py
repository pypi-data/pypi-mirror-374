from enum import Enum

from pydantic import BaseModel, RootModel


class SignalListModel(RootModel[list[str]]):
    "List of signals"


class SampleRatesModel(RootModel[list[int]]):
    "List of sample rates (Hz)"


class RecordingState(str, Enum):
    "Logic analyser recording state"

    IDLE = "idle"
    RECORDING = "recording"


class RecordingStateModel(RootModel[RecordingState]):
    "Model for the response from the tools.logic_analyser.get_recording_state endpoint"


class StartRecordingParams(BaseModel):
    "Parameters for the tools.logic_analyser.start_recording endpoint"

    tool_id: str
    signals: list[str]
    sample_rate_hz: int
    samples: int


class Recording(BaseModel):
    """A recording made with a logic analyser"""

    # The names of the signals that were sampled
    signals: tuple[str, ...]
    sample_rate_hz: int

    # The samples that were taken in the recording.
    # Indexing: samples[sample_number][signal_index]
    # Where signame_index is the index into the signals
    # tuple from above.
    samples: tuple[tuple[bool, ...], ...]
