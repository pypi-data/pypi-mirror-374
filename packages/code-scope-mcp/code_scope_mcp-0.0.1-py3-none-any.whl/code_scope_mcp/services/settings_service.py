"""
Settings management service for the Code Scope MCP server.

This service handles settings information, statistics,
temporary directory management, and settings cleanup operations.
"""

import os
import tempfile
from typing import Dict, Any

from .base_service import BaseService
from ..constants import SETTINGS_DIR


def manage_temp_directory(action: str) -> Dict[str, Any]:
    """
    Manage temporary directory operations.

    This is a standalone function that doesn't require project context.
    Handles the logic for create_temp_directory and check_temp_directory MCP tools.

    Args:
        action: The action to perform ('create' or 'check')

    Returns:
        Dictionary with directory information and operation results

    Raises:
        ValueError: If action is invalid or operation fails
    """
    if action not in ['create', 'check']:
        raise ValueError(f"Invalid action: {action}. Must be 'create' or 'check'")

    temp_dir = os.path.join(tempfile.gettempdir(), SETTINGS_DIR)

    from ..utils import ResponseFormatter
    if action == 'create':
        existed_before = os.path.exists(temp_dir)

        try:
            # Use ProjectSettings to handle directory creation consistently
            from ..project_settings import ProjectSettings
            ProjectSettings("", skip_load=True)

            result = ResponseFormatter.directory_info_response(
                temp_directory=temp_dir,
                exists=os.path.exists(temp_dir),
                is_directory=os.path.isdir(temp_dir)
            )
            result["existed_before"] = existed_before
            result["created"] = not existed_before

            return result

        except (OSError, IOError, ValueError) as e:
            return ResponseFormatter.directory_info_response(
                temp_directory=temp_dir,
                exists=False,
                error=str(e)
            )

    else:  # action == 'check'
        result = ResponseFormatter.directory_info_response(
            temp_directory=temp_dir,
            exists=os.path.exists(temp_dir),
            is_directory=os.path.isdir(temp_dir) if os.path.exists(temp_dir) else False
        )
        result["temp_root"] = tempfile.gettempdir()

        # If the directory exists, list its contents
        if result["exists"] and result["is_directory"]:
            try:
                contents = os.listdir(temp_dir)
                result["contents"] = contents
                result["subdirectories"] = []

                # Check each subdirectory
                for item in contents:
                    item_path = os.path.join(temp_dir, item)
                    if os.path.isdir(item_path):
                        subdir_info = {
                            "name": item,
                            "path": item_path,
                            "contents": os.listdir(item_path) if os.path.exists(item_path) else []
                        }
                        result["subdirectories"].append(subdir_info)

            except (OSError, PermissionError) as e:
                result["error"] = str(e)

        return result





class SettingsService(BaseService):
    """
    Service for managing settings and directory operations.

    This service handles:
    - Settings information and statistics
    - Temporary directory management
    - Settings cleanup operations
    - Configuration data access
    """



    def get_settings_info(self) -> Dict[str, Any]:
        """
        Get comprehensive settings information.

        Handles the logic for get_settings_info MCP tool.

        Returns:
            Dictionary with settings directory, config, stats, and status information
        """
        temp_dir = os.path.join(tempfile.gettempdir(), SETTINGS_DIR)

        from ..utils import ResponseFormatter
        # Check if base_path is set
        if not self.base_path:
            return ResponseFormatter.settings_info_response(
                settings_directory="",
                temp_directory=temp_dir,
                temp_directory_exists=os.path.exists(temp_dir),
                config={},
                stats={},
                exists=False,
                status="not_configured",
                message="Project path not set. Please use set_project_path to set a "
                        "project directory first."
            )

        # Get config and stats
        config = self.settings.load_config() if self.settings else {}
        stats = self.settings.get_stats() if self.settings else {}
        settings_directory = self.settings.settings_path if self.settings else ""
        exists = os.path.exists(settings_directory) if settings_directory else False

        return ResponseFormatter.settings_info_response(
            settings_directory=settings_directory,
            temp_directory=temp_dir,
            temp_directory_exists=os.path.exists(temp_dir),
            config=config,
            stats=stats,
            exists=exists
        )



    def clear_all_settings(self) -> str:
        """
        Clear all settings and cached data.

        Handles the logic for clear_settings MCP tool.

        Returns:
            Success message confirming settings were cleared
        """
        if self.settings:
            self.settings.clear()

        return "Project settings, index, and cache have been cleared."

    def get_settings_stats(self) -> str:
        """
        Get settings statistics as JSON string.

        Handles the logic for settings://stats MCP resource.

        Returns:
            JSON formatted settings statistics
        """
        if not self.settings:
            stats_data = {"error": "Settings not available"}
        else:
            stats_data = self.settings.get_stats()
        from ..utils import ResponseFormatter
        return ResponseFormatter.stats_response(stats_data)
