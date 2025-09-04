#!/usr/bin/env python3
# this_file: src/qtuidoctools/merge_utils.py
"""
YAML and TOC merge utilities for parallel update workflow.

Extracted from the CLI class to keep __main__ focused on argument wiring.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from yaplon import oyaml

from .cli_utils import (
    COLORS,
    console,
    format_user_error,
    log_file_operation,
    log_processing_step,
    repo_relpath,
)


def merge_yaml_files(
    outyamldir: str,
    all_results: list[dict[str, Any]],
    verbose: bool,
    merge_prefer: str = "nonempty",
    merge_strict: bool = False,
) -> None:
    """Merge YAML data from parallel workers into consolidated YAML files with conflict policy."""
    import os

    logger = logging.getLogger("qtuidoctools")
    log_processing_step(
        logger, "YAML merge start", f"Processing {len(all_results)} worker results"
    )

    if not all_results:
        log_processing_step(logger, "YAML merge", "No results to merge", "warning")
        return

    yaml_groups: dict[str, list[dict[str, Any]]] = {}
    successful_yaml_results = 0
    failed_yaml_results = 0

    duplicate_counts: dict[str, int] = {}
    for result in all_results:
        file_name = Path(result["file_path"]).name
        if verbose:
            # Count duplicates by base filename to summarize later
            duplicate_counts[file_name] = duplicate_counts.get(file_name, 0) + 1

        if result["success"] and result["yaml_data"] and result["yaml_filename"]:
            filename = result["yaml_filename"]
            successful_yaml_results += 1
            yaml_groups.setdefault(filename, []).append(result)
        else:
            failed_yaml_results += 1
            if verbose:
                console.print(
                    f"[{COLORS['warning']}]   ⚠️  Skipping {file_name}: not successful or no YAML data[/]"
                )

    if verbose:
        console.print(
            f"[{COLORS['info']}]📊 YAML merge summary: {successful_yaml_results} successful, {failed_yaml_results} failed[/]"
        )
        # Summarize duplicates to keep logs readable (gracefully ignore duplicates)
        dup_summ = ", ".join(
            f"{name}×{count}"
            for name, count in sorted(duplicate_counts.items())
            if count > 1
        )
        if dup_summ:
            console.print(
                f"[{COLORS['muted']}]Duplicates observed (ignored): {dup_summ}[/]"
            )

    if not yaml_groups:
        if verbose:
            console.print(
                f"[{COLORS['warning']}]⚠️  No YAML groups formed - no files will be written[/]"
            )
        return

    if verbose:
        console.print(
            f"[{COLORS['success']}]📊 Formed {len(yaml_groups)} YAML groups: {list(yaml_groups.keys())}[/]"
        )

    # Normalize preference
    prefer = (merge_prefer or "nonempty").lower()
    if prefer not in {"nonempty", "first", "last"}:
        prefer = "nonempty"

    def _choose_value(a, b):
        if prefer == "first":
            return a if a is not None else b
        if prefer == "last":
            return b
        # nonempty default
        if (a in (None, "")) and (b not in (None, "")):
            return b
        if (b in (None, "")) and (a not in (None, "")):
            return a
        return a if a is not None else b

    conflicts: list[str] = []

    for yaml_filename, results in yaml_groups.items():
        yaml_path = os.path.join(outyamldir, yaml_filename)
        if len(results) == 1:
            yaml_data = results[0]["yaml_data"]
        else:
            merged_data: dict[str, Any] = {}
            source_files = []
            for result in results:
                yaml_data = result["yaml_data"]
                source_files.append(repo_relpath(result["file_path"]))
                for key, value in yaml_data.items():
                    if key not in merged_data:
                        merged_data[key] = value
                        continue
                    existing = merged_data[key]
                    if isinstance(existing, dict) and isinstance(value, dict):
                        for prop, newv in value.items():
                            if prop not in existing:
                                existing[prop] = newv
                                continue
                            oldv = existing[prop]
                            if oldv == newv:
                                continue
                            if merge_strict and all(
                                isinstance(x, str) and x.strip() for x in (oldv, newv)
                            ):
                                conflicts.append(
                                    f"{yaml_filename}:{key}.{prop} :: '{oldv}' vs '{newv}'"
                                )
                            existing[prop] = _choose_value(oldv, newv)
                    else:
                        if merge_strict and existing != value:
                            conflicts.append(f"{yaml_filename}:{key} :: '{existing}' vs '{value}'")
                        merged_data[key] = _choose_value(existing, value)
            yaml_data = merged_data
            if verbose:
                console.print(
                    f"[{COLORS['info']}]🔗 Merging[/] {yaml_filename} from {len(results)} files: {', '.join(source_files)}"
                )

        try:
            yaml_text = oyaml.yaml_dumps(
                yaml_data,
                compact=False,
                width=0,
                quote_strings=True,
                block_strings=True,
            )
            with open(yaml_path, "w") as f:
                f.write(yaml_text)
            log_file_operation(logger, "YAML merge save", yaml_path, "success")
        except Exception as e:
            log_file_operation(logger, "YAML merge save", yaml_path, "error", str(e))
            if verbose:
                from .cli_utils import format_user_error

                detailed_error = format_user_error(
                    e, f"Saving YAML file {yaml_filename}"
                )
                console.print(f"[{COLORS['error']}]❌ {detailed_error}[/]")

    if merge_strict and conflicts:
        raise ValueError(
            "Conflicts detected during YAML merge (strict mode):\n"
            + "\n".join(conflicts[:50])
            + ("\n..." if len(conflicts) > 50 else "")
        )
    total_merged = sum(len(results) for results in yaml_groups.values())
    log_processing_step(
        logger,
        "YAML merge complete",
        f"{len(yaml_groups)} output files from {total_merged} source files",
    )


def merge_toc_files(
    tocyaml: str, toc_data_list: list[dict[str, Any]], verbose: bool
) -> None:
    """Merge TOC data from workers and save to a single YAML file."""
    if not toc_data_list:
        return

    merged_toc: dict[str, Any] = {}
    if Path(tocyaml).exists():
        try:
            with open(tocyaml) as f:
                existing_toc = oyaml.read_yaml(f)
                if existing_toc:
                    merged_toc.update(existing_toc)
        except Exception as e:
            if verbose:
                print(f"Warning: Could not read existing TOC file {tocyaml}: {e}")

    def _merge_one(dst: dict[str, Any], src: dict[str, Any]):
        # Deep-merge 'pages' key; shallow-merge others
        for k, v in src.items():
            if k == "pages" and isinstance(v, dict):
                dst.setdefault("pages", {})
                for page, pdata in v.items():
                    dst["pages"][page] = pdata
            else:
                dst[k] = v

    files_merged = 0
    for toc_data in toc_data_list:
        if toc_data:
            _merge_one(merged_toc, toc_data)
            files_merged += 1

    try:
        toc_path = Path(tocyaml)
        toc_path.parent.mkdir(parents=True, exist_ok=True)

        sorted_toc = {}
        for key in sorted(merged_toc.keys()):
            sorted_toc[key] = merged_toc[key]

        yaml_content = oyaml.yaml_dumps(
            sorted_toc,
            compact=False,
            width=0,
            quote_strings=True,
            block_strings=True,
        )
        with open(tocyaml, "w") as f:
            f.write(yaml_content)
        if verbose:
            print(f"Merged TOC data from {files_merged} files into {tocyaml}")
    except Exception as e:
        detailed_error = format_user_error(
            e,
            "Saving table-of-contents file",
            [
                "Check if you have write permissions to the directory",
                "Ensure the output directory exists",
                "Verify there is sufficient disk space",
            ],
        )
        console.print(f"[{COLORS['error']}]❌ {detailed_error}[/]")
