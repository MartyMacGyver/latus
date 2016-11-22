
import os
import time
import logging
import shutil
import sys
import subprocess
import threading

import latus.logger
import latus.util
import latus.crypto
import latus.preferences
import latus.sync
import latus.nodedb
import latus.folders


def logger_init(log_folder):
    if latus.logger.log:
        print('WARNING: logger already set up')
    else:
        latus.logger.init(log_folder)
    latus.logger.set_console_log_level(logging.INFO)
    latus.logger.set_file_log_level(logging.DEBUG)
    latus.logger.log.info('logger_init')


def get_python_exe():
    if latus.util.is_windows():
        bin_folder = 'Scripts'
    else:
        bin_folder = 'bin'
    return os.path.join('venv', bin_folder, 'python')


# waits for a file to exist
# set "to_exist" parameter to False if you want to wait until the file does NOT exist
def wait_for_file(file_path, to_exist=True):
    time_out_sec = 20
    sleep_time_sec = 0.1
    time_out_count_down = time_out_sec / sleep_time_sec

    if to_exist:
        message = ''
    else:
        message = ' not'

    while (to_exist ^ os.path.exists(file_path)) and time_out_count_down > 0:
        time.sleep(sleep_time_sec)
        time_out_count_down -= 1
    if time_out_count_down <= 0:
        print('timeout waiting for %s to%s exist' % (file_path, message))
        return False
    return True


def write_preferences(node_id, data_root, latus_key):
    """
    :param node_id: name of this node
    :param data_root: folder this test is using for all its data
    :param latus_key: the (shared) latus crypto key
    :return: folder where the preferences file resides
    """
    app_data_folder = get_app_data_folder(data_root, node_id)
    pref = latus.preferences.Preferences(app_data_folder, True)
    pref.set_node_id(node_id)
    # this folder is shared across all the nodes to emulate cloud sync
    pref.set_cloud_root(os.path.join(data_root, 'cloud'))
    pref.set_latus_folder(get_latus_folder(data_root, node_id))
    pref.set_crypto_key(latus_key)
    return app_data_folder


def get_latus_folder(root, node_id):
    return os.path.join(root, node_id, 'latus')  # give us our own folder


def get_app_data_folder(root, node_id):
    return os.path.join(root, node_id, 'appdata')  # give us our own folder


def get_file_name(node_id):
    return node_id + '.txt'


class SyncThread(threading.Thread):
    """
    Run the sync in a separate process.  This is necessary since the watchdog module and/or the
    underlying OS doesn't work well if there are multiple watchers watching the same path in the same process
    (i.e. we can't merely start multiple syncs in the test process - we have to create multiple separate processes).
    """
    def __init__(self, app_data_folder):
        self.app_data_folder = app_data_folder
        self.sync_process = None
        super().__init__()

    def run(self):
        cmd = '%s %s -a %s -v' % (sys.executable, os.path.join('latus', 'sync.py'), self.app_data_folder)
        latus.logger.log.info(cmd)
        self.sync_process = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE)

    def request_exit(self):
        self.sync_process.communicate(b'\n\r')  # emulate 'enter' key (one of these should do it)


def clean():
    """
    clean up the test data
    :return:
    """
    path = get_data_root()
    try_count = 10
    while os.path.exists(path) and try_count:
        try:
            shutil.rmtree(path)
        except PermissionError as e:
            # log isn't set up yet, so just print
            print('can not rmtree %s - retrying' % path)
            print(str(e))
            time.sleep(1)
            try_count -= 1
    assert(try_count > 0)
    if try_count == 0:
        exit('clean failed')


def write_to_file(dir_path, file_name, contents, subdir=None):
    if subdir:
        p = os.path.join(dir_path, subdir, file_name)
    else:
        p = os.path.join(dir_path, file_name)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w") as f:
        f.write(contents)
        f.close()
    return p


sha512 = {
    'a' : "1f40fc92da241694750979ee6cf582f2d5d7d28e18335de05abc54d0560e0f5302860c652bf08d560252aa5e74210546f369fbbbce8c12cfc7957b2652fe9a75"
}


def get_data_root():
    return os.path.abspath(os.path.join('test_latus', 'data'))


def root_test_gui_wizard():
    return os.path.join('test_latus', 'test_gui_wizard')