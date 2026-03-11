from sentence_transformers import SentenceTransformer
import torch
from dataclasses import dataclass
import gzip

DEFAULT_EMBEDDER = "BAAI/bge-m3"  # 1024-dim
DEFAULT_VECTOR_SIZE = 1024




@dataclass
class PointShardWriter:
    out_dir: str
    shard_size: int = 10_000
    basename: str = "points"
    count: int = 0
    shard_idx: int = 0
    fh = None

    def _open_new(self):
        

        if self.fh:
            self.fh.close()
        path = f"{self.out_dir}/{self.basename}_{self.shard_idx:05d}.jsonl.gz"
        self.fh = gzip.open(path, "wt", encoding="utf-8")
        self.shard_idx += 1
        return path

    def write_many(self, point_dicts):
        import json

        if not point_dicts:
            return
        if self.fh is None or self.count % self.shard_size == 0:
            self._open_new()
        for pd in point_dicts:
            self.fh.write(json.dumps(pd, ensure_ascii=False) + "\n")
            self.count += 1

    def close(self):
        if self.fh:
            self.fh.close()
            self.fh = None


class Embedder:
    def __init__(self, model_name: str = "BAAI/bge-m3"):
        self.model = SentenceTransformer(model_name)
        if torch.cuda.is_available():
            self.device = "cuda"
            self.model = self.model.to("cuda")
            print("[Embedder] Using NVIDIA CUDA")
        elif torch.backends.mps.is_available():
            self.device = "mps"
            self.model = self.model.to("mps")
            print("[Embedder] Using Apple MPS")
        else:
            self.device = "cpu"
            print("[Embedder] Using CPU")

    def encode(self, texts: list[str], batch_size: int = 1024) -> list[list[float]]:
        if not texts:
            return []
        vecs = self.model.encode(
            texts,
            device=self.device,
            normalize_embeddings=True,
            show_progress_bar=False,
            batch_size=batch_size,
        )
        return vecs.tolist()


