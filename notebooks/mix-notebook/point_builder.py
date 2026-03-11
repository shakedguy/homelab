from typing import Any
from embedder import Embedder
from summorizations import norm_text, stable_id, summarize_row, sparse_tokens
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
)
from qdrant_client.http import models as qm

def row_to_payload(row: dict[str, Any]) -> dict[str, Any]:
    # Convenience flags
    has_ads = any(
        row.get(k) is not None
        for k in ["ads_watched", "ads_watched_cnt", "ads_watched_cnt_lt"]
    )
    is_payer = (row.get("ltv") or 0) > 0

    payload = {
        "table": "user_daily_metrics_agg",
        "entity": "user_day",
        "user_id": row.get("user_id"),
        "date_dim": row.get("date_dim"),  # ISO string
        "country_code": row.get("country_code"),
        "platform": row.get("platform"),
        "quality_level": row.get("quality_level"),
        "dcx": norm_text(row.get("current_dcx")),
        "scx": norm_text(row.get("current_scx")),
        "has_ads": has_ads,
        "is_payer": is_payer,
    }
    return payload


@retry(reraise=True, stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=8))
def build_point(args):
    row, text, vec = args
    sp = sparse_tokens(text)
    pid = stable_id(str(row.get("user_id")), str(row.get("date_dim")))

    return qm.PointStruct(
        id=pid,
        vector={
            "text": vec,
            "bm25": qm.SparseVector(indices=list(sp.keys()), values=list(sp.values())),
        },
        payload={"text": text, **row_to_payload(row)},
    )


def build_points(
    rows: list[dict[str, Any]], embedder: Embedder
) -> list[qm.PointStruct]:
    texts = [summarize_row(row) for row in rows]
    if not texts:
        return []
    dense = embedder.encode(texts)

    return [build_point(args) for args in zip(rows, texts, dense)]


def build_point_dict(row: dict, text: str, dense_vec: list[float]) -> dict:
    sp = sparse_tokens(text)
    pid = stable_id(str(row.get("user_id")), str(row.get("date_dim")))
    return {
        "id": pid,
        "vector": {
            "text": dense_vec,
            "bm25": {"indices": list(sp.keys()), "values": list(sp.values())},
        },
        "payload": {"text": text, **row_to_payload(row)},
    }