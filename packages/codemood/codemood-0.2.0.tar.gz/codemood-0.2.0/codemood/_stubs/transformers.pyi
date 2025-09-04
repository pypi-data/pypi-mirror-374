from typing import Any, Dict, List, Literal, overload

class Pipeline:
    def __call__(
        self, inputs: str, *args: Any, **kwargs: Any
    ) -> List[Dict[str, Any]]: ...
    def __getitem__(self, idx: int) -> Dict[str, Any]: ...

@overload
def pipeline(
    task: Literal["sentiment-analysis"],
    model: str | None = None,
    *args: Any,
    **kwargs: Any,
) -> Pipeline: ...
@overload
def pipeline(
    task: str, model: str | None = None, *args: Any, **kwargs: Any
) -> Pipeline: ...
