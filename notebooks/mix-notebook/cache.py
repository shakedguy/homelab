from pathlib import Path
from datetime import date
import pandas as pd

class Cache:
    def __init__(self, root: Path):
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    def day_path(self, d: date) -> Path:
        return self.root / f"day={d.isoformat()}.parquet"

    def exists(self, d: date) -> bool:
        return self.day_path(d).exists()

    def write_day(self, d: date, df: pd.DataFrame) -> None:
        p = self.day_path(d)
        if not df.empty:
            df.to_parquet(p, index=False)
        else:
            # write empty marker file
            p.touch()

    def read_day(self, d: date) -> pd.DataFrame:
        p = self.day_path(d)
        if not p.exists():
            return pd.DataFrame()
        try:
            return pd.read_parquet(p)
        except Exception:
            return pd.DataFrame()


cache = Cache(Path("./cache/bq_user_daily_metrics"))