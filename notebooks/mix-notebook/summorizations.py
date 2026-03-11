import hashlib
import math
import re
import uuid
from typing import Any



def norm_text(s: str | None) -> str:
    if not s:
        return ""
    # collapse whitespace, strip quotes artifacts
    s = s.strip()
    s = re.sub(r"\s+", " ", s)
    s = s.strip('"\'')
    return s


def stable_id(*parts: str) -> str:
    h = hashlib.md5("|".join(parts).encode()).hexdigest()
    return str(uuid.UUID(hex=h.lower()))


# --------------------------- Summarization -----------------------------


# Dynamic field categories for summarization (non-null values only)
CATEGORIES: dict[str, list[str]] = {
    # Engagement & sessions
    "engagement": [
        "sessions_cnt",
        "sessions_duration_sec_sum",
        "last_active_days_7",
        "sessions_duration_bucket",
    ],
    # Economy: coins & rolls
    "economy": [
        "coins_startday", "coins_enday", "coins_in_sum", "coins_out_sum",
        "coins_out_stolen_sum", "coins_out_build_sum", "coins_out_rapair_sum",
        "rolls_startday", "rolls_enday", "rolls_in_sum", "rolls_out_sum",
        "not_enough_rolls_cnt", "out_of_rolls_cnt",
    ],
    # Progression
    "progression": [
        "crowns_startday", "crowns_enday", "kingdom_id_startday", "kingdom_id_enday",
        "buildings_completed", "items_built_sum", "items_fixed_sum",
    ],
    # Monetization
    "monetization": [
        "revenues_sum", "net_revenues_sum", "srv_revenues_sum", "ltv", "net_ltv",
        "trx_cnt", "trx_lt", "srv_trx_cnt", "dice_dreams_plus_purchase_amount",
        "dice_dreams_plus_purchase_net_amount", "coins_purchased_sum", "rolls_purchased_sum",
        "apple_stripe_purchase_amount", "apple_stripe_purchase_net_amount",
        "app_charge_purchase_amount", "app_charge_purchase_net_amount",
        "last_purchase_ts", "became_vip_date", "dormant_payer",
    ],
    # Ads
    "ads": [
        "ads_watched_cnt", "ads_watched_cnt_lt", "ad_revenues", "ad_revenues_lt",
    ],
    # Context / experiments
    "context": [
        "current_dcx", "current_scx", "test_group_names", "client_app_version_enday",
        "quality_level", "device_model",
    ],
}


def _nn(x: Any) -> bool:
    """Non-null checker used by summarization."""
    if x is None:
        return False
    if isinstance(x, float) and math.isnan(x):
        return False
    return True


def _fmt(x: Any) -> str:
    """Compact number formatter used by summarization."""
    if isinstance(x, int):
        return str(x)
    try:
        xf = float(x)
        return str(int(xf)) if abs(xf - int(xf)) < 1e-9 else f"{xf:.2f}"
    except Exception:
        return norm_text(str(x))


def _summarize_category(cat: str, row: dict[str, Any]) -> str | None:
    """Return a compact phrase(s) for a given category using `CATEGORIES` field list.
    Only includes fields present and non-null in the row.
    Special-cases certain families (coins/rolls/crowns) for arrow-style deltas.
    """
    flds = CATEGORIES.get(cat, [])

    # Quick presence check
    has_any = any(_nn(row.get(k)) for k in flds)
    if not has_any:
        return None

    parts: list[str] = []

    if cat == "engagement":
        if _nn(row.get("sessions_cnt")):
            parts.append(f"sessions={_fmt(row['sessions_cnt'])}")
        if _nn(row.get("sessions_duration_sec_sum")):
            parts.append(f"dur={_fmt(row['sessions_duration_sec_sum'])}s")
        if _nn(row.get("last_active_days_7")):
            parts.append(f"active7d={_fmt(row['last_active_days_7'])}")

    elif cat == "economy":
        # coins
        if _nn(row.get("coins_startday")) and _nn(row.get("coins_enday")):
            parts.append(f"coins {_fmt(row['coins_startday'])}→{_fmt(row['coins_enday'])}")
        io = []
        if _nn(row.get("coins_in_sum")):
            io.append(f"in={_fmt(row['coins_in_sum'])}")
        if _nn(row.get("coins_out_sum")):
            io.append(f"out={_fmt(row['coins_out_sum'])}")
        if _nn(row.get("coins_out_stolen_sum")):
            io.append(f"stolen={_fmt(row['coins_out_stolen_sum'])}")
        if io:
            parts.append(" ".join(io))
        # rolls
        if _nn(row.get("rolls_startday")) and _nn(row.get("rolls_enday")):
            parts.append(f"rolls {_fmt(row['rolls_startday'])}→{_fmt(row['rolls_enday'])}")
        if _nn(row.get("rolls_in_sum")):
            parts.append(f"rin={_fmt(row['rolls_in_sum'])}")
        # crowns
        if _nn(row.get("crowns_startday")) and _nn(row.get("crowns_enday")):
            parts.append(f"crowns {_fmt(row['crowns_startday'])}→{_fmt(row['crowns_enday'])}")
        # other economy fields listed in CATEGORIES will be appended as key=value
        for k in ("coins_out_build_sum", "coins_out_rapair_sum", "rolls_out_sum", "not_enough_rolls_cnt",
                  "out_of_rolls_cnt"):
            if k in flds and _nn(row.get(k)):
                parts.append(f"{k}={_fmt(row[k])}")

    elif cat == "progression":
        if _nn(row.get("kingdom_id_startday")) and _nn(row.get("kingdom_id_enday")):
            parts.append(f"kingdom {_fmt(row['kingdom_id_startday'])}→{_fmt(row['kingdom_id_enday'])}")
        if _nn(row.get("buildings_completed")):
            parts.append(f"buildings_completed={_fmt(row['buildings_completed'])}")
        if _nn(row.get("items_built_sum")):
            parts.append(f"items_built={_fmt(row['items_built_sum'])}")
        if _nn(row.get("items_fixed_sum")):
            parts.append(f"items_fixed={_fmt(row['items_fixed_sum'])}")
        if _nn(row.get("crowns_startday")) and _nn(row.get("crowns_enday")) and not any(
                p.startswith("crowns ") for p in parts):
            parts.append(f"crowns {_fmt(row['crowns_startday'])}→{_fmt(row['crowns_enday'])}")

    elif cat == "monetization":
        for k in [
            "revenues_sum", "net_revenues_sum", "srv_revenues_sum", "ltv", "net_ltv",
            "trx_cnt", "trx_lt", "srv_trx_cnt",
            "dice_dreams_plus_purchase_amount", "dice_dreams_plus_purchase_net_amount",
            "coins_purchased_sum", "rolls_purchased_sum",
            "apple_stripe_purchase_amount", "apple_stripe_purchase_net_amount",
            "app_charge_purchase_amount", "app_charge_purchase_net_amount",
        ]:
            if k in flds and _nn(row.get(k)):
                parts.append(f"{k}={_fmt(row[k])}")
        if _nn(row.get("last_purchase_ts")):
            parts.append(f"last_purchase={norm_text(str(row['last_purchase_ts']))}")
        if _nn(row.get("became_vip_date")):
            parts.append(f"vip={norm_text(str(row['became_vip_date']))}")
        if _nn(row.get("dormant_payer")):
            parts.append(f"dormant_payer={_fmt(row['dormant_payer'])}")

    elif cat == "ads":
        if _nn(row.get("ads_watched_cnt")):
            parts.append(f"ads={_fmt(row['ads_watched_cnt'])}")
        if _nn(row.get("ads_watched_cnt_lt")):
            parts.append(f"ads_lt={_fmt(row['ads_watched_cnt_lt'])}")
        if _nn(row.get("ad_revenues")) or _nn(row.get("ad_revenues_lt")):
            val = row.get("ad_revenues") if _nn(row.get("ad_revenues")) else row.get("ad_revenues_lt")
            parts.append(f"ad_rev={_fmt(val)}")

    elif cat == "context":
        if _nn(row.get("current_dcx")):
            parts.append(f"dcx={norm_text(row['current_dcx'])}")
        if _nn(row.get("current_scx")):
            parts.append(f"scx={norm_text(row['current_scx'])}")
        if _nn(row.get("test_group_names")):
            parts.append(f"group={norm_text(row['test_group_names'])}")
        if _nn(row.get("client_app_version_enday")):
            parts.append(f"ver={norm_text(row['client_app_version_enday'])}")
        if _nn(row.get("quality_level")):
            parts.append(f"quality={norm_text(row['quality_level'])}")
        if _nn(row.get("device_model")):
            parts.append(f"device={norm_text(row['device_model'])}")

    # Fallback: if nothing special constructed, attach generic key=value pairs
    if not parts:
        gen = [f"{k}={_fmt(row[k])}" for k in flds if _nn(row.get(k))]
        if gen:
            parts.append(" ".join(gen))

    return " ".join(parts) if parts else None


def summarize_row(row: dict[str, Any]) -> str:
    """Deterministic compact summary for embedding, built dynamically from CATEGORIES."""
    row.pop("___id___", None)  # remove internal ID if present
    header = (
        f"user_daily_metrics_agg • {row.get('date_dim')} • user={row.get('user_id')} "
        f"• {row.get('country_code')}/{row.get('platform')} "
        f"• ver={row.get('client_app_version_enday')} • quality={row.get('quality_level')}"
    )

    parts: list[str] = [header]

    # Preserve insertion order of CATEGORIES (Py3.7+ dicts are ordered)
    for cat in CATEGORIES.keys():
        frag = _summarize_category(cat, row)
        if frag:
            parts.append(frag)

    text = " | ".join(p for p in parts if p)
    MAX = 500
    if len(text) > MAX:
        text = text[:MAX - 20] + " …"
    return text


def sparse_tokens(text: str) -> dict[int, float]:
    """Very light sparse vector from token frequencies.
    In production, consider a BM25 builder or Qdrant text-sparse encoder.
    """
    from collections import Counter

    toks = re.findall(r"[a-zA-Z0-9_:\-/\.]+", text.lower())
    c = Counter(toks)
    # map tokens to pseudo-indices by hashing; keep small dictionary
    return {hash(t) % 2_000_000: float(freq) for t, freq in c.items()}
