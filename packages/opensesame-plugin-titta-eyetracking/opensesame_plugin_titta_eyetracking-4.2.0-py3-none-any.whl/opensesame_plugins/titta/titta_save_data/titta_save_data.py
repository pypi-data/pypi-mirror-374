"""
This file is part of OpenSesame.

This work is licensed under the Creative Commons Attribution 4.0 International License.
To view a copy of this license, visit http://creativecommons.org/licenses/by/4.0/
or send a letter to Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.
"""

__author__ = "Bob Rosbag"
__license__ = "CC BY 4.0"

from libopensesame.py3compat import *
from libopensesame.item import Item
from libqtopensesame.items.qtautoplugin import QtAutoPlugin
from libopensesame.exceptions import OSException
from libopensesame.oslogging import oslogger
import pandas as pd


class TittaSaveData(Item):

    def reset(self):
        self.var.tsv_export = 'no'

    def prepare(self):
        super().prepare()
        self._init_var()
        self._check_init()

    def run(self):
        self._check_stop()
        self.set_item_onset()
        self.experiment.tracker.save_data()
        
        if self.tsv_export == 'yes' and self.experiment.titta_dummy_mode == 'no':
            df_gaze = pd.read_hdf(f'{self.experiment.titta_file_name}.h5', 'gaze')
            df_msg = pd.read_hdf(f'{self.experiment.titta_file_name}.h5', 'msg')
            df_external_signal = pd.read_hdf(f'{self.experiment.titta_file_name}.h5', 'external_signal')
            df_calibration_history = pd.read_hdf(f'{self.experiment.titta_file_name}.h5', 'calibration_history')
            df_merged = pd.concat([df_gaze, df_msg, df_external_signal])
            df_merged.sort_values("system_time_stamp", axis = 0, ascending = True,
                                 inplace = True, na_position ='last')

            df_gaze.to_csv(f'{self.experiment.titta_file_name}_gaze.tsv', sep='\t')
            df_msg.to_csv(f'{self.experiment.titta_file_name}_msg.tsv', sep='\t')
            df_external_signal.to_csv(f'{self.experiment.titta_file_name}_external_signal.tsv', sep='\t')
            df_calibration_history.to_csv(f'{self.experiment.titta_file_name}_calibration_history.tsv', sep='\t')
            df_merged.to_csv(f'{self.experiment.titta_file_name}_data_merged.tsv', sep='\t')

    def _check_init(self):
        if hasattr(self.experiment, "titta_dummy_mode"):
            self.dummy_mode = self.experiment.titta_dummy_mode
            self.verbose = self.experiment.titta_verbose
        else:
            raise OSException('You should have one instance of `Titta Init` at the start of your experiment')

    def _check_stop(self):
        if not hasattr(self.experiment, "titta_stop_recording"):
            raise OSException(
                    '`Titta Stop Recording` item is missing')
        elif self.experiment.titta_recording:
                raise OSException(
                        'Titta still recording, you first have to stop recording before saving data')

    def _init_var(self):
        self.tsv_export = self.var.tsv_export

    def _show_message(self, message):
        oslogger.debug(message)
        if self.verbose == 'yes':
            print(message)


class QtTittaSaveData(TittaSaveData, QtAutoPlugin):

    def __init__(self, name, experiment, script=None):
        TittaSaveData.__init__(self, name, experiment, script)
        QtAutoPlugin.__init__(self, __file__)

