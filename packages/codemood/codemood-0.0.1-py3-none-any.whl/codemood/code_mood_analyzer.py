import os
import warnings
import re
from typing import Any, Dict, List, cast

try:
    from transformers import pipeline
except ImportError:
    pipeline = None  # type: ignore
    Pipeline = None  # type: ignore

try:
    from huggingface_hub import InferenceClient as HFInferenceClient
except ImportError:
    HFInferenceClient = None  # type: ignore


class CodeMoodAnalyzer:
    def __init__(
        self,
        model: str = (
            "distilbert/distilbert-base-uncased-finetuned-sst-2-english"
        ),
    ):
        self.model = model
        self.local_model: Any = None
        self.client: Any = None

        # Step 1: Try local transformers pipeline
        if pipeline:
            try:
                self.local_model = pipeline(  # type: ignore
                    "sentiment-analysis", model=self.model  # type: ignore
                )

            except Exception as e:
                warnings.warn(f"Local pipeline failed: {e}")
                self.local_model = None

        # Step 2: Prepare HuggingFace client (fallback)
        if HFInferenceClient:
            token = os.getenv("HF_TOKEN")
            if token:
                try:
                    self.client = HFInferenceClient(api_key=token)  # type: ignore
                except Exception as e:
                    warnings.warn(f"HuggingFace client init failed: {e}")
                    self.client = None

    def _analyze_single(self, text: str) -> Dict[str, Any]:
        """Run sentiment on a single string using available backend."""
        if self.local_model:
            try:
                return self.local_model(text)[0]  # type: ignore[index]
            except Exception:
                pass

        if self.client:
            try:
                result = self.client.text_classification(  # type: ignore
                    text, model=self.model
                )
                result = cast(List[Dict[str, Any]], result)
                if isinstance(result, list) and result:
                    return result[0]
                return {"label": "NEUTRAL", "score": 0.5}
            except Exception:
                pass

        return {"label": "NEUTRAL", "score": 0.5}

    def analyze(self, code: str) -> Dict[str, Any]:
        """Analyze mood of given code snippet with funny explanation."""
        main_result = self._analyze_single(code)
        label = main_result["label"]
        score = main_result["score"]

        # Token-level scan
        tokens = re.split(r"[^a-zA-Z0-9_]+", code)
        tokens = [t for t in tokens if t]

        positive_triggers, negative_triggers = [], []
        for tok in tokens:
            r = self._analyze_single(tok)
            if r["label"] == "POSITIVE" and r["score"] > 0.7:
                positive_triggers.append(tok)
            elif r["label"] == "NEGATIVE" and r["score"] > 0.7:
                negative_triggers.append(tok)

        if label == "POSITIVE" and positive_triggers:
            reason = (
                f"Model got happy because it saw "
                f"{', '.join(set(positive_triggers))} 🎉"
            )
        elif label == "NEGATIVE" and negative_triggers:
            reason = (
                f"Model got sad because it saw "
                f"{', '.join(set(negative_triggers))} 😢"
            )
        else:
            reason = "Model is confused but still picked a mood 🤷"

        return {"label": label, "score": score, "reason": reason}

    def explain_sentiment(self, code: str) -> Dict[str, Any]:
        """Alias for analyze(), kept for clarity and backwards compatibility."""
        return self.analyze(code)
