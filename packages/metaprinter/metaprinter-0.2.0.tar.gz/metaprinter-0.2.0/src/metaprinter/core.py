"""
SPSS Metadata Utility Module
============================
A utility module for printing and exporting SPSS data metadata using pyreadstat and polars.

This module provides functions to:
- Display comprehensive metadata from SPSS files
- Export metadata summaries to text files
- Handle both basic and extended metadata fields

Author: [Your Name]
Version:
Dependencies: pyreadstat, polars, pandas
"""

import json
import polars as pl
import pandas as pd
import os
from pathlib import Path
from io import StringIO
import sys


def _prepare_metadata_summary(df, meta, include_all=False):
    """
    Internal function to prepare metadata summary.
    Used by both print_metadata and export_metadata to avoid code duplication.

    Parameters:
    -----------
    df : polars.DataFrame or pandas.DataFrame
        The dataframe containing the SPSS data
    meta : pyreadstat metadata object
        The metadata object returned by pyreadstat.read_sav()
    include_all : bool, default False
        Whether to include all available metadata fields

    Returns:
    --------
    tuple
        (polars.DataFrame, dict) - The metadata summary DataFrame and category counts
    """
    # Convert to Polars if it's a Pandas DataFrame
    if isinstance(df, pd.DataFrame):
        df = pl.from_pandas(df)

    # Count categorical labels for each variable
    cat_counts = {
        var: len(labels) for var, labels in meta.variable_value_labels.items()
    }

    # Create pretty-formatted JSON strings for value labels
    value_labels_pretty = [
        json.dumps(
            meta.variable_value_labels.get(col, {}), indent=2, ensure_ascii=False
        )
        if meta.variable_value_labels.get(col)
        else ""
        for col in df.columns
    ]

    # Calculate column_n excluding nulls and empty strings for string columns
    column_n_values = []
    for c in df.columns:
        if df[c].dtype in [pl.Utf8, pl.String, pl.Categorical]:
            # For string columns, exclude both nulls and empty strings
            count = len(df.filter(pl.col(c).is_not_null() & (pl.col(c) != "")))
        else:
            # For non-string columns, just count non-nulls
            count = len(df.filter(pl.col(c).is_not_null()))
        column_n_values.append(count)

    # Build the metadata summary based on include_all parameter
    if include_all:
        # Build complete dictionary with all metadata fields
        summary_dict = {
            "column": df.columns,
            "dtype": df.dtypes,
            "column_n": column_n_values,
            "n_categories": [cat_counts.get(c, 0) for c in df.columns],
            "column_label": meta.column_labels,
            "value_labels": value_labels_pretty,
            "variable_measure": [
                meta.variable_measure.get(c, "unknown") for c in df.columns
            ],
            "variable_format": [
                meta.original_variable_types.get(c, "") for c in df.columns
            ],
            "missing_ranges": [meta.missing_ranges.get(c, []) for c in df.columns],
            "missing_user_values": [
                meta.missing_user_values.get(c, []) for c in df.columns
            ],
            "variable_alignment": [
                meta.variable_alignment.get(c, "unknown") for c in df.columns
            ],
            "variable_storage_width": [
                meta.variable_storage_width.get(c, None) for c in df.columns
            ],
            "variable_display_width": [
                meta.variable_display_width.get(c, None) for c in df.columns
            ],
        }
    else:
        # Basic metadata summary
        summary_dict = {
            "column": df.columns,
            "dtype": df.dtypes,
            "column_n": column_n_values,
            "n_categories": [cat_counts.get(c, 0) for c in df.columns],
            "column_label": meta.column_labels,
            "value_labels": value_labels_pretty,
        }

    return pl.DataFrame(summary_dict), cat_counts


def _format_metadata_output(meta, summary, include_all, show_all_columns, max_width):
    """
    Internal function to format metadata for output.

    Parameters:
    -----------
    meta : pyreadstat metadata object
        The metadata object returned by pyreadstat.read_sav()
    summary : polars.DataFrame
        The prepared metadata summary DataFrame
    include_all : bool
        Whether all metadata fields are included
    show_all_columns : bool
        Whether to show all columns without truncation
    max_width : int
        Maximum table width in characters

    Returns:
    --------
    str
        The formatted metadata output as a string
    """
    output = StringIO()

    # File-level metadata header
    print("=" * 60, file=output)
    print("SPSS FILE METADATA", file=output)
    print("=" * 60, file=output)
    print(f"File encoding   : {meta.file_encoding!r}", file=output)
    print(f"Number of cols  : {meta.number_columns}", file=output)
    print(f"Number of rows  : {meta.number_rows}", file=output)
    print(f"Table name      : {meta.table_name!r}", file=output)
    print(f"File label      : {meta.file_label!r}", file=output)
    print(f"Notes           : {meta.notes!r}", file=output)
    print(file=output)

    # Variable metadata header
    print("VARIABLE METADATA", file=output)
    if include_all:
        print("(Showing all available metadata fields)", file=output)
    else:
        print(
            "(Showing basic metadata - use include_all=True for all fields)",
            file=output,
        )
    print("=" * 60, file=output)

    # Configure display options
    config_options = {"tbl_width_chars": max_width, "fmt_str_lengths": 5000}

    if show_all_columns:
        config_options.update({"tbl_cols": -1, "tbl_rows": -1})

    # Format the summary table
    with pl.Config(**config_options):
        print(summary, file=output)

    return output.getvalue()


def print_metadata(df, meta, show_all_columns=True, max_width=222, include_all=False):
    """
    Print a comprehensive metadata summary for SPSS data loaded with pyreadstat.

    Parameters:
    -----------
    df : polars.DataFrame or pandas.DataFrame
        The dataframe containing the SPSS data
    meta : pyreadstat metadata object
        The metadata object returned by pyreadstat.read_sav()
    show_all_columns : bool, default True
        Whether to show all columns without truncation
    max_width : int, default 222
        Maximum table width in characters
    include_all : bool, default False
        Whether to include all available metadata fields. If False, only shows basic fields
        (column, dtype, column_n, n_categories, column_label, value_labels)

    Returns:
    --------
    polars.DataFrame
        The metadata summary table for further use if needed

    Example:
    --------
    >>> import pyreadstat
    >>> df, meta = pyreadstat.read_sav('your_file.sav')
    >>> metadata_summary = print_metadata(df, meta)
    """
    # Prepare the metadata summary
    summary, _ = _prepare_metadata_summary(df, meta, include_all)

    # Format and print the output
    output = _format_metadata_output(
        meta, summary, include_all, show_all_columns, max_width
    )
    print(output, end="")

    return summary


def export_metadata(
    df, meta, filename=None, show_all_columns=True, max_width=222, include_all=False
):
    """
    Export SPSS metadata summary to a text file in the downloads folder.

    Parameters:
    -----------
    df : polars.DataFrame or pandas.DataFrame
        The dataframe containing the SPSS data
    meta : pyreadstat metadata object
        The metadata object returned by pyreadstat.read_sav()
    filename : str, optional
        Custom filename (without extension). If None, uses "metadata_summary"
    show_all_columns : bool, default True
        Whether to show all columns without truncation
    max_width : int, default 222
        Maximum table width in characters
    include_all : bool, default False
        Whether to include all available metadata fields. If False, only shows basic fields
        (column, dtype, column_n, n_categories, column_label, value_labels)

    Returns:
    --------
    str or None
        The full path where the file was saved, or None if export failed

    Example:
    --------
    >>> import pyreadstat
    >>> df, meta = pyreadstat.read_sav('your_file.sav')
    >>> export_path = export_metadata(df, meta, filename="my_metadata", include_all=True)
    """
    # Prepare the metadata summary
    summary, _ = _prepare_metadata_summary(df, meta, include_all)

    # Format the output
    content = _format_metadata_output(
        meta, summary, include_all, show_all_columns, max_width
    )

    # Determine the downloads folder path
    downloads_path = Path.home() / "Downloads"
    if not downloads_path.exists():
        # Fallback to current directory if Downloads folder doesn't exist
        downloads_path = Path.cwd()

    # Set filename
    if filename is None:
        filename = "metadata_summary"

    # Ensure .txt extension
    if not filename.endswith(".txt"):
        filename = f"{filename}.txt"

    full_path = downloads_path / filename

    # Write to file
    try:
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"✅ Metadata summary exported successfully to: {full_path}")
        return str(full_path)

    except Exception as e:
        print(f"❌ Error saving file: {e}")
        return None


def print_and_export_metadata(
    df,
    meta,
    export_filename=None,
    show_all_columns=True,
    max_width=222,
    include_all=False,
):
    """
    Convenience function that both prints and exports SPSS metadata summary.

    Parameters:
    -----------
    df : polars.DataFrame or pandas.DataFrame
        The dataframe containing the SPSS data
    meta : pyreadstat metadata object
        The metadata object returned by pyreadstat.read_sav()
    export_filename : str, optional
        Custom filename for export (without extension). If None, uses "metadata_summary"
    show_all_columns : bool, default True
        Whether to show all columns without truncation
    max_width : int, default 222
        Maximum table width in characters
    include_all : bool, default False
        Whether to include all available metadata fields. If False, only shows basic fields
        (column, dtype, column_n, n_categories, column_label, value_labels)

    Returns:
    --------
    tuple
        (polars.DataFrame, str) - The metadata summary table and export file path

    Example:
    --------
    >>> import pyreadstat
    >>> df, meta = pyreadstat.read_sav('your_file.sav')
    >>> summary, export_path = print_and_export_metadata(df, meta, include_all=True)
    """
    # Print to console
    summary = print_metadata(df, meta, show_all_columns, max_width, include_all)

    # Export to file
    export_path = export_metadata(
        df, meta, export_filename, show_all_columns, max_width, include_all
    )

    return summary, export_path


# Optional: Add version info and other module metadata
__version__ = "0.2.0"
__author__ = "Your Name"
__all__ = ["print_metadata", "export_metadata", "print_and_export_metadata"]


if __name__ == "__main__":
    # Example usage when run as a script
    print("SPSS Metadata Utility Module")
    print(f"Version: {__version__}")
    print("\nThis module provides functions for working with SPSS metadata.")
    print("\nUsage:")
    print("  import pyreadstat")
    print("  from spss_metadata_utils import print_metadata, export_metadata")
    print("  ")
    print("  df, meta = pyreadstat.read_sav('your_file.sav')")
    print("  ")
    print("  # Print basic metadata")
    print("  print_metadata(df, meta)")
    print("  ")
    print("  # Export with all metadata fields")
    print("  export_metadata(df, meta, include_all=True)")
