"""
Resource processing for Zeeker database operations.

This module handles loading resource modules, executing data functions,
applying transformations, and inserting data into SQLite databases.
"""

import importlib.util
import inspect
import sqlite3
from pathlib import Path
from typing import Any, Dict, List

import sqlite_utils

from ..schema import SchemaManager
from ..types import ValidationResult
from .async_executor import AsyncExecutor


class ResourceProcessor:
    """Handles processing of individual resources and fragments."""

    def __init__(self, resources_path: Path, schema_manager: SchemaManager):
        """Initialize resource processor.

        Args:
            resources_path: Path to resources directory
            schema_manager: Schema manager instance for tracking
        """
        self.resources_path = resources_path
        self.schema_manager = schema_manager
        self.async_executor = AsyncExecutor()

    def process_resource(self, db: sqlite_utils.Database, resource_name: str) -> ValidationResult:
        """Process a single resource using sqlite-utils for robust data insertion.

        Benefits of sqlite-utils over raw SQL:
        - Automatic table creation with correct schema
        - Type inference from data (no manual column type guessing)
        - JSON support for complex data structures
        - Proper error handling and validation
        - No SQL injection risks

        Args:
            db: sqlite-utils Database instance
            resource_name: Name of the resource to process

        Returns:
            ValidationResult with processing results
        """
        result = ValidationResult(is_valid=True)

        # Load and validate resource module
        module_result = self._load_resource_module(resource_name)
        if not module_result.is_valid:
            return module_result

        module = module_result.data

        try:
            # Get the fetch_data function
            if not hasattr(module, "fetch_data"):
                result.is_valid = False
                result.errors.append(f"Resource '{resource_name}' missing fetch_data() function")
                return result

            fetch_data = getattr(module, "fetch_data")

            # Check if table already exists to pass to fetch_data
            existing_table = db[resource_name] if db[resource_name].exists() else None

            # Fetch the data
            raw_data = self.async_executor.call_fetch_data(
                fetch_data, existing_table, resource_name=resource_name
            )

            if not isinstance(raw_data, list):
                result.is_valid = False
                result.errors.append(f"fetch_data() in '{resource_name}' must return a list")
                return result

            if not raw_data:
                result.info.append(f"No data returned for resource '{resource_name}' - skipping")
                return result

            # Apply transformation if available
            transformed_data = self._apply_transformation(
                module, raw_data, resource_name, "transform_data"
            )
            if transformed_data is None:
                result.is_valid = False
                result.errors.append(f"Data transformation failed for '{resource_name}'")
                return result

            # Validate transformed data structure
            validation_result = self._validate_data_structure(transformed_data, resource_name)
            if not validation_result.is_valid:
                return validation_result

            # Insert data using sqlite-utils
            table = db[resource_name]

            # Track schema for conflict detection
            if not existing_table:  # New table
                self.schema_manager.track_new_table_schema(db, resource_name, transformed_data)

            # Insert all data at once for better performance
            table.insert_all(transformed_data, replace=False)

            result.info.append(
                f"Processed {len(transformed_data)} records for resource '{resource_name}'"
            )

        except sqlite3.IntegrityError as e:
            result.is_valid = False
            result.errors.append(f"Database integrity error in '{resource_name}': {e}")
        except Exception as e:
            result.is_valid = False
            result.errors.append(f"Failed to process resource '{resource_name}': {e}")

        return result

    def process_fragments_data(
        self,
        db: sqlite_utils.Database,
        resource_name: str,
        module: Any,
        main_data_context: List[Dict[str, Any]] = None,
    ) -> ValidationResult:
        """Process fragments data for a resource that supports document fragmentation.

        Args:
            db: sqlite-utils Database instance
            resource_name: Name of the main resource
            module: The imported resource module
            main_data_context: Raw data from fetch_data() to avoid duplicate fetches (optional)

        Returns:
            ValidationResult with processing results
        """
        result = ValidationResult(is_valid=True)
        fragments_table_name = f"{resource_name}_fragments"

        try:
            if not hasattr(module, "fetch_fragments_data"):
                result.is_valid = False
                result.errors.append(
                    f"Resource '{resource_name}' missing fetch_fragments_data() function"
                )
                return result

            fetch_fragments_data = getattr(module, "fetch_fragments_data")

            # Check if fragments table already exists
            existing_fragments_table = (
                db[fragments_table_name] if db[fragments_table_name].exists() else None
            )

            # Fetch fragments data with optional main data context
            raw_fragments = self._call_fragments_function(
                fetch_fragments_data, existing_fragments_table, main_data_context
            )

            if not isinstance(raw_fragments, list):
                result.is_valid = False
                result.errors.append(
                    f"fetch_fragments_data() in '{resource_name}' must return a list"
                )
                return result

            if not raw_fragments:
                result.info.append(f"No fragments data for '{resource_name}' - skipping")
                return result

            # Apply transformation if available
            transformed_fragments = self._apply_transformation(
                module, raw_fragments, resource_name, "transform_fragments_data"
            )
            if transformed_fragments is None:
                result.is_valid = False
                result.errors.append(f"Fragment transformation failed for '{resource_name}'")
                return result

            # Validate fragments data structure
            validation_result = self._validate_data_structure(
                transformed_fragments, f"{resource_name} fragments"
            )
            if not validation_result.is_valid:
                return validation_result

            # Insert fragments data using sqlite-utils
            fragments_table = db[fragments_table_name]

            # Track schema for conflict detection
            if not existing_fragments_table:  # New table
                self.schema_manager.track_new_table_schema(
                    db, fragments_table_name, transformed_fragments
                )

            # Insert all fragments at once for better performance
            fragments_table.insert_all(transformed_fragments, replace=False)

            result.info.append(
                f"Processed {len(transformed_fragments)} fragments for resource '{resource_name}'"
            )

        except sqlite3.IntegrityError as e:
            result.is_valid = False
            result.errors.append(f"Database integrity error in '{resource_name}' fragments: {e}")
        except Exception as e:
            result.is_valid = False
            result.errors.append(f"Failed to process fragments for '{resource_name}': {e}")

        return result

    def _load_resource_module(self, resource_name: str) -> ValidationResult:
        """Load a resource module dynamically.

        Args:
            resource_name: Name of the resource to load

        Returns:
            ValidationResult with module in data field if successful
        """
        result = ValidationResult(is_valid=True)

        resource_file = self.resources_path / f"{resource_name}.py"
        if not resource_file.exists():
            result.is_valid = False
            result.errors.append(f"Resource file not found: {resource_file}")
            return result

        try:
            # Dynamically import the resource module
            spec = importlib.util.spec_from_file_location(resource_name, resource_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            result.data = module

        except Exception as e:
            result.is_valid = False
            result.errors.append(f"Failed to load resource module '{resource_name}': {e}")

        return result

    def _call_fragments_function(
        self,
        fetch_fragments_data,
        existing_fragments_table,
        main_data_context,
    ) -> List[Dict[str, Any]]:
        """Call fetch_fragments_data with proper signature handling."""
        sig = inspect.signature(fetch_fragments_data)

        if len(sig.parameters) >= 2 and main_data_context is not None:
            # Enhanced signature: fetch_fragments_data(existing_fragments_table, main_data_context)
            try:
                return self.async_executor.call_fetch_fragments_data(
                    fetch_fragments_data, existing_fragments_table, main_data_context
                )
            except TypeError:
                # Fallback to old signature if function doesn't accept context
                return self.async_executor.call_fetch_fragments_data(
                    fetch_fragments_data, existing_fragments_table
                )
        else:
            # Original signature: fetch_fragments_data(existing_fragments_table)
            return self.async_executor.call_fetch_fragments_data(
                fetch_fragments_data, existing_fragments_table
            )

    def _apply_transformation(
        self, module: Any, data: List[Dict[str, Any]], resource_name: str, transform_func_name: str
    ) -> List[Dict[str, Any]] | None:
        """Apply transformation function if available.

        Args:
            module: The resource module
            data: Data to transform
            resource_name: Name of resource for error messages
            transform_func_name: Name of transformation function

        Returns:
            Transformed data or None if transformation failed
        """
        if hasattr(module, transform_func_name):
            try:
                transform_func = getattr(module, transform_func_name)
                return transform_func(data)
            except Exception:
                return None
        else:
            return data

    def _validate_data_structure(
        self, data: List[Dict[str, Any]], context: str
    ) -> ValidationResult:
        """Validate that data has the correct structure.

        Args:
            data: Data to validate
            context: Context string for error messages

        Returns:
            ValidationResult indicating if data is valid
        """
        result = ValidationResult(is_valid=True)

        if not isinstance(data, list):
            result.is_valid = False
            result.errors.append(f"Data for '{context}' must be a list")
            return result

        if not all(isinstance(item, dict) for item in data):
            result.is_valid = False
            result.errors.append(f"All items in '{context}' data must be dictionaries")

        return result
