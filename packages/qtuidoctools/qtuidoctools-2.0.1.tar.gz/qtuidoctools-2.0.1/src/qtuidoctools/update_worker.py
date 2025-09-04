#!/usr/bin/env python3
# this_file: src/qtuidoctools/update_worker.py
"""
Worker function for parallel UI processing.

Kept separate from __main__ to ensure it's importable for multiprocessing
on platforms that use spawn (e.g., Windows). The function signature and
return format mirror the previous inlined implementation.
"""

from __future__ import annotations

import time
from typing import Any

from .qtui import UIDoc
from .cli_utils import setup_loguru_rich_logging, repo_relpath
from loguru import logger as _loguru


def process_ui_file_worker(
    ui_file_path: str,
    tocyaml: str | None,
    outyamldir: str,
    emptytoyaml: bool,
    alwayssaveyaml: bool,
    logLevel: str,
    nosavexml: bool,
    tooltipstoxml: bool,
    tooltipstoyaml: bool,
    replaceinyaml: bool,
    verbose: bool = False,
) -> dict[str, Any]:
    """Process a single UI file in isolation and return a structured result dict.

    Signature matches the current CLI call site in __main__.py
    """
    import os
    import traceback

    start_time = time.time()
    result: dict[str, Any] = {
        "file_path": ui_file_path,
        "success": False,
        "toc_data": None,
        "yaml_data": None,
        "yaml_filename": None,
        "error_message": None,
        "error_type": None,
        "error_traceback": None,
        "processing_time": 0.0,
        "widgets_found": 0,
        "xml_saved": False,
    }

    try:
        # Configure worker logging similarly to main process
        setup_loguru_rich_logging(verbose=bool(verbose), quiet=False)
        # Construct UIDoc
        uid = UIDoc(uipath=ui_file_path, yamldir=outyamldir, logLevel=logLevel)
        # Configure based on parameters
        if tocyaml:
            uid.tocpath = tocyaml
        uid.rebuildStatusTipsInXml = True
        uid.replaceToolTipsInXml = bool(tooltipstoxml)
        uid.replaceToolTipsInYaml = bool(tooltipstoyaml)
        uid.updateYaml = True
        uid.replaceNamInYaml = bool(replaceinyaml)
        uid.outempty = bool(emptytoyaml)
        if alwayssaveyaml:
            uid.modifiedYaml = True

        # Build TOC first if requested, then update
        if tocyaml:
            uid.updateToc()
        uid.updateXmlAndYaml()

        if verbose:
            file_disp = repo_relpath(ui_file_path)
            _loguru.debug(f"{file_disp}:> updateXmlAndYaml completed")

        # Widgets processed (approximate)
        if getattr(uid, "root", None) is not None:
            result["widgets_found"] = len(uid.root.findall(".//widget")) + len(
                uid.root.findall(".//action")
            )

        # Save XML file if requested
        if not nosavexml:
            uid.saveXml()
            result["xml_saved"] = True

        # Collect YAML data for merging (don't write files in worker)
        if outyamldir:
            result["yaml_filename"] = f"{uid.docname}.yaml"
            yaml_data = getattr(uid, "tips", {})
            if verbose:
                _loguru.debug(
                    f"{uid.docname}:> Raw tips attribute has {len(yaml_data)} keys: {list(yaml_data.keys())[:5]}"
                )

            if yaml_data:

                def ordered_dict_to_dict(obj):
                    if isinstance(obj, dict):
                        return {k: ordered_dict_to_dict(v) for k, v in obj.items()}
                    if isinstance(obj, dict):
                        return {k: ordered_dict_to_dict(v) for k, v in obj.items()}
                    if isinstance(obj, list):
                        return [ordered_dict_to_dict(item) for item in obj]
                    return obj

                result["yaml_data"] = ordered_dict_to_dict(yaml_data)
                if verbose:
                    _loguru.debug(
                        f"{uid.docname}:> Converted YAML data has {len(result['yaml_data'])} keys"
                    )
            else:
                result["yaml_data"] = {}
                if verbose:
                    _loguru.debug(
                        f"{uid.docname}:> No YAML data found in tips attribute"
                    )

            # Validate YAML structure
            try:
                import yaml

                yaml_str = yaml.dump(result["yaml_data"], default_flow_style=False)
                yaml.safe_load(yaml_str)
                if verbose:
                    _loguru.debug(
                        f"{uid.docname}:> YAML data validation passed - {len(result['yaml_data'])} keys"
                    )
            except Exception as yaml_err:
                raise ValueError(
                    f"Generated YAML data is invalid: {yaml_err}"
                ) from yaml_err

        # Extract TOC data for later merging
        if tocyaml:
            result["toc_data"] = getattr(uid, "toc", None)

        result["success"] = True
        result["processing_time"] = time.time() - start_time
        return result

    except Exception as e:
        result["error_message"] = str(e)
        result["error_type"] = type(e).__name__
        result["error_traceback"] = traceback.format_exc()
        result["processing_time"] = time.time() - start_time

        if verbose:
            _loguru.error(
                f"Worker error for {ui_file_path}: {result['error_type']}: {result['error_message']}"
            )
            _loguru.debug(f"Traceback:\n{result['error_traceback']}")

        return result
