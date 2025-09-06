from pathlib import Path
import unittest
import tempfile

import polars as pl
from polars_darwin_core import DarwinCoreLazyFrame


class TestLfCsv(unittest.TestCase):
    def test_read_darwin_core_csv(self) -> None:
        # Create a tiny Darwin Core‐like CSV in a temporary directory
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            csv_path = tmp_path / "dwc.csv"
            csv_path.write_text("id\tkingdom\n1\tAnimalia\n2\tPlantae")

            lf = DarwinCoreLazyFrame.from_csv(csv_path)
            self.assertIsInstance(lf, DarwinCoreLazyFrame)

            df: pl.DataFrame = lf._inner.collect()
            self.assertEqual(df.shape, (2, 2))  # two rows, two columns
            self.assertEqual(df["kingdom"].to_list(), ["Animalia", "Plantae"])

    def test_read_darwin_core_parquet(self) -> None:
        # Create a tiny Darwin Core‐like Parquet file in a temporary directory
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            parquet_path = tmp_path / "dwc.parquet"
            df = pl.DataFrame({"id": [1, 2], "kingdom": ["Animalia", "Plantae"]})
            df.write_parquet(parquet_path)

            lf = DarwinCoreLazyFrame.from_parquet(parquet_path)
            self.assertIsInstance(lf, DarwinCoreLazyFrame)

            collected_df: pl.DataFrame = lf._inner.collect()
            self.assertEqual(collected_df.shape, (2, 2))
            self.assertEqual(collected_df["kingdom"].to_list(), ["Animalia", "Plantae"])
