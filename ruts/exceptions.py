from anyts.exceptions import (
    AnyTSError,
    DataFileError as DataFileError,
    DatasetNotFoundError as DatasetNotFoundError,
    DownloadError as DownloadError,
    ParameterError as ParameterError,
    SourceError as SourceError,
    SourceTypeError as SourceTypeError,
    UnknownStatError as UnknownStatError,
)

# Классы самого ядра, чтобы их ловили и ошибки, поднятые его кодом
RutsError = AnyTSError
