from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Type
import xml.etree.ElementTree as ET
from dataclasses import dataclass

import polars as pl

from polars_darwin_core.darwin_core import kingdom_data_type

__all__ = [
    "DarwinCoreLazyFrame",
]


@dataclass
class _Meta:
    """A private class to hold parsed metadata from meta.xml."""

    core_file: str
    separator: str
    quote_char: str
    encoding: str
    has_header: bool
    columns: List[str]
    default_fields: Dict[str, str]


class DarwinCoreLazyFrame:
    """A thin wrapper around :pyclass:`polars.LazyFrame` for Darwin Core CSVs.

    The class intentionally exposes (and delegates to) the full *polars* lazy
    API while giving the object a domain-specific identity that tools like
    linters and type-checkers can understand.
    """

    # Columns that need a type override.
    # Polars can infer most types, but dates, datetimes, and booleans stored as
    # strings need to be specified.
    SCHEMA_OVERRIDES: Dict[str, Type[pl.DataType] | pl.DataType] = {
        "kingdom": kingdom_data_type,
        # Dates and datetimes
        # "modified": pl.Datetime,
        # "eventDate": pl.Datetime,
        # "dateIdentified": pl.Date,
        # "georeferencedDate": pl.Date,
        # "lastInterpreted": pl.Datetime,
        # "lastParsed": pl.Datetime,
        # "lastCrawled": pl.Datetime,
        # Booleans
        "hasCoordinate": pl.Boolean,
        "hasGeospatialIssues": pl.Boolean,
        "repatriated": pl.Boolean,
    }

    def __init__(self, inner: pl.LazyFrame):
        """Initialize the Darwin Core LazyFrame wrapper.

        Parameters
        ----------
        inner : pl.LazyFrame
            The inner LazyFrame to wrap
        """
        self._inner = inner

    @classmethod
    def from_csv(
        cls,
        path: str | Path,
    ) -> DarwinCoreLazyFrame:
        """Scan a Darwin Core CSV lazily.
        This is a very light wrapper around :pyfunc:`polars.scan_csv` that returns a
        domain-specific :class:`DarwinCoreLazyFrame` instead of a plain
        :class:`polars.LazyFrame`.
        Parameters
        ----------
        path : str | Path
            Path to the CSV file
        **scan_csv_kwargs
            Additional keyword arguments passed to pl.scan_csv
        """

        inner = pl.scan_csv(
            path,
            schema_overrides=DarwinCoreLazyFrame.SCHEMA_OVERRIDES,
            quote_char=None,
            separator="\t",
        )
        return DarwinCoreLazyFrame(inner)

    @classmethod
    def from_parquet(
        cls,
        path: str | Path,
    ) -> DarwinCoreLazyFrame:
        """Scan a Darwin Core Parquet file lazily.
        This is a very light wrapper around :pyfunc:`polars.scan_parquet` that returns a
        domain-specific :class:`DarwinCoreLazyFrame` instead of a plain
        :class:`polars.LazyFrame`.
        Parameters
        ----------
        path : str | Path
            Path to the Parquet file
        """

        inner = pl.scan_parquet(
            path,
        )
        return DarwinCoreLazyFrame(inner)

    @staticmethod
    def _parse_meta(meta_path: Path) -> _Meta:
        """Parse the meta.xml file and return a dictionary of settings.

        This method reads the Darwin Core archive's metafile (meta.xml) to extract
        parameters needed to correctly parse the core data file. The parsing is
        guided by the Darwin Core text guide.

        Returns
        -------
        _Meta
            A dataclass instance containing the parsed metadata.
        """
        tree = ET.parse(meta_path)
        root = tree.getroot()

        # Handle XML namespace if present
        ns = {"dwc": "http://rs.tdwg.org/dwc/text/"}

        # Try with namespace first, then without
        core_elem = root.find("dwc:core", ns)
        if core_elem is None:
            core_elem = root.find(".//core")
        if core_elem is None:
            raise ValueError("meta.xml does not contain <core> element")

        # file location – in <files><location>relative/path</location></files>
        files_elem = core_elem.find(".//files")
        if files_elem is None:
            files_elem = core_elem.find("dwc:files", ns)
        if files_elem is None:
            raise ValueError("<core> missing <files>")

        location_elem = files_elem.find(".//location")
        if location_elem is None:
            location_elem = files_elem.find("dwc:location", ns)
        if location_elem is None or not location_elem.text:
            raise ValueError("<files> missing <location>")
        core_file = location_elem.text.strip()

        # attributes from the <core> element, with defaults from the guide
        # fieldsTerminatedBy: Delimiter between fields (e.g., "," or "\t").
        separator = core_elem.get("fieldsTerminatedBy", ",")
        if separator == "\\t":
            separator = "\t"

        # fieldsEnclosedBy: Character to enclose fields (e.g., '"').
        quote_char = core_elem.get("fieldsEnclosedBy", '"')

        # encoding: Character encoding of the file (e.g., "utf-8").
        encoding = core_elem.get("encoding", "utf-8")

        # ignoreHeaderLines: Number of initial lines to skip.
        ignore_header = int(core_elem.get("ignoreHeaderLines", "0"))
        has_header = ignore_header >= 1

        # fields and default values
        fields: List[str] = []
        default_fields: Dict[str, str] = {}

        field_elems = core_elem.findall(".//field")
        if not field_elems:
            field_elems = core_elem.findall("dwc:field", ns)

        for field_elem in field_elems:
            term_uri = field_elem.get("term")
            if term_uri is None:
                continue

            term = term_uri.rsplit("/", 1)[-1].rsplit("#", 1)[-1]
            index_str = field_elem.get("index")

            # A <field> with an "index" maps a column in the data file.
            if index_str is not None:
                try:
                    idx = int(index_str)
                except ValueError:
                    continue
                if len(fields) <= idx:
                    fields.extend([""] * (idx - len(fields) + 1))
                fields[idx] = term
            # A <field> without "index" but with "default" defines a constant
            # value for that term for all rows.
            else:
                default_value = field_elem.get("default")
                if default_value is not None:
                    default_fields[term] = default_value

        # some meta.xml include <id index="0" /> that represents the record id
        id_elem = core_elem.find(".//id")
        if id_elem is None:
            id_elem = core_elem.find("dwc:id", ns)

        if id_elem is not None:
            idx2 = id_elem.get("index")
            if idx2 is not None:
                try:
                    idx = int(idx2)
                    if len(fields) <= idx:
                        fields.extend([""] * (idx - len(fields) + 1))
                    # id doesn't have a term; choose "id"
                    if not fields[idx]:
                        fields[idx] = "id"
                except (ValueError, IndexError):
                    pass  # Or log a warning

        # fill any empty column names with fallback names
        final_fields = [name if name else f"col_{i}" for i, name in enumerate(fields)]

        return _Meta(
            core_file=core_file,
            has_header=has_header,
            separator=separator,
            columns=final_fields,
            quote_char=quote_char,
            encoding=encoding,
            default_fields=default_fields,
        )

    @classmethod
    def from_archive(
        cls, path: str | Path, **scan_csv_kwargs: Any
    ) -> DarwinCoreLazyFrame:  # noqa: D401
        """Scan an *unpacked* Darwin Core Archive directory lazily.
        Parameters
        ----------
        path:
            Path to a directory that contains at least ``meta.xml`` and the core
            data file referenced from it.
        **scan_csv_kwargs:
            Extra keyword arguments forwarded to :pyfunc:`polars.scan_csv` (e.g.
            ``infer_schema_length``).
        Returns
        -------
        DarwinCoreLazyFrame
        """

        base_dir = Path(path)
        meta_path = base_dir / "meta.xml"
        if not meta_path.exists():
            raise FileNotFoundError("meta.xml not found in archive directory")

        meta = cls._parse_meta(meta_path)
        data_path = base_dir / meta.core_file

        schema_from_meta = {
            col: cls.SCHEMA_OVERRIDES[col]
            for col in meta.columns
            if col in cls.SCHEMA_OVERRIDES
        }
        scan_csv_kwargs.setdefault("schema_overrides", {}).update(schema_from_meta)

        if meta.encoding.upper() != "UTF-8":
            raise NotImplementedError(
                f"Only UTF-8 encoding is supported, got {meta.encoding}"
            )

        inner = pl.scan_csv(
            data_path,
            separator=meta.separator,
            has_header=meta.has_header,
            new_columns=meta.columns if not meta.has_header else None,
            quote_char=meta.quote_char,
            encoding="utf8",
            **scan_csv_kwargs,
        )

        # Add default fields
        for col_name, value in meta.default_fields.items():
            inner = inner.with_columns(pl.lit(value).alias(col_name))

        return DarwinCoreLazyFrame(inner)
