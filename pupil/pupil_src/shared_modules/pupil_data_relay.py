"""
(*)~---------------------------------------------------------------------------
Pupil - eye tracking platform
Copyright (C) 2012-2019 Pupil Labs

Distributed under the terms of the GNU
Lesser General Public License (LGPL v3.0).
See COPYING and COPYING.LESSER for license details.
---------------------------------------------------------------------------~(*)
"""

from plugin import System_Plugin_Base
import zmq_tools


class Pupil_Data_Relay(System_Plugin_Base):
    """
    """

    def __init__(self, g_pool):
        super().__init__(g_pool)
        self.order = 0.01
        self.gaze_pub = zmq_tools.Msg_Streamer(
            self.g_pool.zmq_ctx, self.g_pool.ipc_pub_url
        )
        self.pupil_sub = zmq_tools.Msg_Receiver(
            self.g_pool.zmq_ctx, self.g_pool.ipc_sub_url, topics=("pupil",)
        )

    def recent_events(self, events):
        recent_pupil_data = []
        recent_gaze_data = []
        while self.pupil_sub.new_data:
            topic, pupil_datum = self.pupil_sub.recv()
            recent_pupil_data.append(pupil_datum)
            new_gaze_data = self.g_pool.active_gaze_mapping_plugin.on_pupil_datum(
                pupil_datum
            )
            for gaze_datum in new_gaze_data:
                self.gaze_pub.send(gaze_datum)
            recent_gaze_data.extend(new_gaze_data)

        events["pupil"] = recent_pupil_data
        events["gaze"] = recent_gaze_data
