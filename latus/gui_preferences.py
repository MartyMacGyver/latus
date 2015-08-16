
import os
import logging

from PyQt5 import QtWidgets, QtCore

import latus.logger
import latus.sync
import latus.preferences
import latus.util
import latus.const
import latus.crypto
import latus.gui_wizard


class LineUI:
    """
    Set up the folder widgets
    """
    def __init__(self, name, value, method=None, button_text='Select...'):
        self.label = QtWidgets.QLabel(name + ':')
        self.line = QtWidgets.QLineEdit(value)
        self.line.setMinimumWidth(600)  # swag
        self.select_button = QtWidgets.QDialogButtonBox()
        self.line.setReadOnly(True)  # guide user via dialog boxes - don't allow them to just type anything in
        if method:
            self.select_button.addButton(button_text, QtWidgets.QDialogButtonBox.AcceptRole)
            self.select_button.accepted.connect(method)

    def layout(self, grid, column):
        grid.addWidget(self.label, column, 0)
        grid.addWidget(self.line, column, 1)
        grid.addWidget(self.select_button, column, 2)

    def get(self):
        return self.line.text()


class CheckBoxUI:
    """
    Set up a check box widgets
    """
    def __init__(self, name, value, method=None):
        self.check_box = QtWidgets.QCheckBox(name)
        if method:
            self.check_box.stateChanged.connect(method)


class PreferencesDialog(QtWidgets.QDialog):
    def __init__(self, latus_appdata_folder):
        latus.logger.log.info('starting PreferencesDialog')
        super().__init__()
        grid_layout = QtWidgets.QGridLayout()

        self.pref = latus.preferences.Preferences(latus_appdata_folder)
        self.latus_folder = LineUI('Latus folder', self.pref.get_latus_folder(), self.new_folder)
        self.cloud_folder = LineUI('Cloud Folder', self.pref.get_cloud_root(), self.new_folder)
        self.node_id = LineUI('Node ID', self.pref.get_node_id())
        self.blank = QtWidgets.QLabel('')

        ok_buttonBox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok)
        ok_buttonBox.accepted.connect(self.ok)
        cancel_buttonBox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Cancel)
        cancel_buttonBox.rejected.connect(self.cancel)

        self.latus_folder.layout(grid_layout, 0)
        self.cloud_folder.layout(grid_layout, 1)
        self.node_id.layout(grid_layout, 3)
        grid_layout.addWidget(self.blank, 4, 0)
        grid_layout.addWidget(ok_buttonBox, 5, 0)
        grid_layout.addWidget(cancel_buttonBox, 5, 1, alignment=QtCore.Qt.AlignLeft)  # kind of cheating on the layout
        grid_layout.setColumnStretch(1, 1)  # path column
        self.setLayout(grid_layout)

        self.setWindowTitle("Preferences")

    def ok(self):
        self.pref.set_latus_folder(self.latus_folder.get())
        self.pref.set_cloud_root(self.cloud_folder.get())
        self.pref.set_new_keys()
        self.close()

    def cancel(self):
        self.close()

    def new_folder(self):
        f = QtWidgets.QFileDialog.getExistingDirectory()
        return f


if __name__ == '__main__':
    import sys
    temp_dir = 'temp'
    latus.logger.init(os.path.join(temp_dir, 'log'))
    latus.logger.set_console_log_level(logging.INFO)

    app = QtWidgets.QApplication(sys.argv)

    preferences_dialog = PreferencesDialog('temp')
    preferences_dialog.show()
    preferences_dialog.exec_()