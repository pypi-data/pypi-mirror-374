"""
Nextcloud sync plugin for Taskinator.

This plugin adds functionality to synchronize tasks with Nextcloud.
"""

from .nextcloud_plugin import NextCloudSyncPlugin 


# This function is required for plugin discovery
def get_plugin():
    """Get the plugin instance."""
    return NextCloudSyncPlugin ()
