"""
(*)~---------------------------------------------------------------------------
Pupil - eye tracking platform
Copyright (C) 2012-2019 Pupil Labs

Distributed under the terms of the GNU
Lesser General Public License (LGPL v3.0).
See COPYING and COPYING.LESSER for license details.
---------------------------------------------------------------------------~(*)
"""

import abc

from pyglui import ui

from task_manager import TaskManager
from plugin import Analysis_Plugin_Base


class VideoExporter(TaskManager, Analysis_Plugin_Base, abc.ABC):
    """
    Base for video exporting plugins. Every time the user hits "export",
    the method export_data gets called
    """

    @abc.abstractmethod
    def export_data(self, export_range, export_dir):
        pass

    def on_notify(self, notification):
        if notification["subject"] == "should_export":
            self.export_data(notification["range"], notification["export_dir"])

    def customize_menu(self):
        self.menu.append(
            ui.Info_Text(
                "The export can be found in the exports folder, under the recording directory."
            )
        )
        self.menu.append(
            ui.Info_Text("Press the export button or type 'e' to start the export.")
        )
