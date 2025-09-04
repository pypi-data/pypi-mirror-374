from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Protocol, Sequence, runtime_checkable

# ---------------------------------------------------------------------
# Protocol
# ---------------------------------------------------------------------


@runtime_checkable
class Embedder(Protocol):
    """Embedding interface used by QMem."""

    dim: int

    def encode(self, texts: List[str]) -> List[List[float]]:
        """Return one vector per input string (len(vector) == self.dim)."""
        ...


# ---------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------


def _chunks(seq: Sequence[str], size: int) -> Iterable[Sequence[str]]:
    for i in range(0, len(seq), size):
        yield seq[i : i + size]


def _l2_normalize(vec: List[float]) -> List[float]:
    s = sum(x * x for x in vec) ** 0.5
    if s == 0.0:
        return vec
    return [x / s for x in vec]


def _ensure_dim(vec: List[float], wanted: int) -> List[float]:
    """Trim or pad so we always return the configured dimension."""
    n = len(vec)
    if n == wanted:
        return vec
    if n > wanted:
        return vec[:wanted]
    return vec + [0.0] * (wanted - n)


# ---------------------------------------------------------------------
# OpenAI
# ---------------------------------------------------------------------


@dataclass
class _OpenAIConfig:
    model: str
    api_key: str
    dim: int
    batch_size: int = 128
    normalize: bool = False


class OpenAIEmbedder:
    """
    OpenAI embedding backend.

    Notes:
    - "text-embedding-3-small" => 1536 dims
    - "text-embedding-3-large" => 3072 dims
    """

    def __init__(self, model: str, api_key: str, dim: int, *, batch_size: int = 128, normalize: bool = False) -> None:
        if not api_key:
            raise ValueError("OpenAI API key is required for OpenAI embeddings")

        try:
            # Lazy import so users on MiniLM don't need the dependency installed.
            from openai import OpenAI  # type: ignore
        except Exception as e:
            raise RuntimeError(
                "OpenAI backend requires the 'openai' package. Install with:\n"
                "  pip install openai"
            ) from e

        self._cfg = _OpenAIConfig(model=model, api_key=api_key, dim=dim, batch_size=batch_size, normalize=normalize)
        self.client = OpenAI(api_key=api_key)
        self.dim = dim

    def encode(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []

        out: List[List[float]] = []
        for batch in _chunks(texts, self._cfg.batch_size):
            resp = self.client.embeddings.create(model=self._cfg.model, input=list(batch))
            for d in resp.data:
                vec = list(d.embedding)
                if self._cfg.normalize:
                    vec = _l2_normalize(vec)
                out.append(_ensure_dim(vec, self._cfg.dim))
        return out


# ---------------------------------------------------------------------
# MiniLM (Hugging Face Inference API — NO DOWNLOADS)
# ---------------------------------------------------------------------


@dataclass
class _HFAPIConfig:
    model: str
    token: str
    dim: int
    batch_size: int = 256
    normalize: bool = False


class MiniLMEmbedder:
    """
    Hosted MiniLM via Hugging Face Inference API.

    - No local model download.
    - Requires: `pip install huggingface_hub>=0.24`
    - Default model: sentence-transformers/all-MiniLM-L6-v2 (384 dims)
    """

    def __init__(self, model: str, token: str, dim: int, *, batch_size: int = 256, normalize: bool = False) -> None:
        if not token:
            raise ValueError("Hugging Face API key is required for MiniLM (HF) embeddings")
        try:
            from huggingface_hub import InferenceClient  # type: ignore
        except Exception as e:
            raise RuntimeError(
                "HF backend requires 'huggingface_hub'. Install with:\n"
                "  pip install huggingface_hub>=0.24"
            ) from e

        self._cfg = _HFAPIConfig(model=model, token=token, dim=dim, batch_size=batch_size, normalize=normalize)
        self.client = InferenceClient(token=token)
        self.dim = dim

    def _extract_embeddings(self, resp) -> List[List[float]]:
        """
        Be tolerant to return shapes across hub versions:
        - Either returns List[List[float]]
        - Or Dict[str, Any] with key 'embeddings'
        """
        if isinstance(resp, dict) and "embeddings" in resp:
            return resp["embeddings"]  # type: ignore[return-value]
        return resp  # assume already List[List[float]]

    def encode(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []

        out: List[List[float]] = []
        for batch in _chunks(texts, self._cfg.batch_size):
            resp = self.client.embeddings(model=self._cfg.model, inputs=list(batch))
            embs = self._extract_embeddings(resp)
            for v in embs:
                vec = list(v)
                if self._cfg.normalize:
                    vec = _l2_normalize(vec)
                out.append(_ensure_dim(vec, self._cfg.dim))
        return out


# ---------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------


def build_embedder(cfg) -> Embedder:
    """
    Construct the appropriate embedder from a QMemConfig-like object.

    Expected fields on cfg:
        - embed_provider in {"openai", "minilm"}
        - embed_model: str
        - embed_dim: int
        - openai_api_key: Optional[str] (if provider == "openai")
        - hf_api_key: Optional[str] (if provider == "minilm")
    """
    if cfg.embed_provider == "openai":
        return OpenAIEmbedder(cfg.embed_model, cfg.openai_api_key or "", cfg.embed_dim)
    if cfg.embed_provider == "minilm":
        # Use hosted MiniLM via Hugging Face Inference API (no downloads)
        return MiniLMEmbedder(cfg.embed_model, getattr(cfg, "hf_api_key", "") or "", cfg.embed_dim)
    raise ValueError(f"Unsupported embed provider: {cfg.embed_provider!r}")
