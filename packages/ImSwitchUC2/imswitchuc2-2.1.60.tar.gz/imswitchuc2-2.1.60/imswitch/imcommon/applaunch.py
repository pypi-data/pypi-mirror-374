import logging
import os
import sys
import traceback
import time
import threading
# somewhere after all your variables & functions exist
try:
    from ipykernel.embed import embed_kernel   # pip install ipykernel
except ImportError:
    embed_kernel = None

from .model import dirtools, pythontools, initLogger
from imswitch.imcommon.framework import Signal, Thread
from imswitch import IS_HEADLESS
if not IS_HEADLESS:
    from qtpy import QtCore, QtGui, QtWidgets
    from .view.guitools import getBaseStyleSheet
    from PyQt5.QtCore import Qt
    from PyQt5.QtWidgets import QApplication
else:
    from psygnal import emit_queued


def prepareApp():
    """ This function must be called before any views are created. """
    if IS_HEADLESS:
        """We won't have any GUI, so we don't need to prepare the app."""
        return None
    # Initialize exception handling
    pythontools.installExceptHook()

    # Set logging levels
    logging.getLogger('pyvisa').setLevel(logging.WARNING)
    logging.getLogger('lantz').setLevel(logging.WARNING)

    # Create app
    os.environ['IMSWITCH_FULL_APP'] = '1'  # Indicator that non-plugin version of ImSwitch is used
    os.environ['PYQTGRAPH_QT_LIB'] = 'PyQt5'  # Force Qt to use PyQt5
    os.environ['HDF5_USE_FILE_LOCKING'] = 'FALSE'  # Force HDF5 to not lock files
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    # TODO: Some weird combination of the below settings may help us to scale Napari?
    # Set environment variables for high DPI scaling
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    #os.environ["QT_SCALE_FACTOR"] = ".8"  # Adjust this value as needed
    from PyQt5.QtCore import Qt
    from PyQt5.QtWidgets import QApplication
    # Set application attributes
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)  # Fixes Napari issues
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_DisableHighDpiScaling, True) # proper scaling on Mac?
    #QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)
    # https://stackoverflow.com/questions/72131093/pyqt5-qwebengineview-doesnt-load-url
    # The following element (sandbox) is to keep the app from crashing when using QWebEngineView
    app = QtWidgets.QApplication(['', '--no-sandbox'])
    app.setStyleSheet("QWidget { font-size: 9pt; }")  # Smaller default font
    app.setWindowIcon(QtGui.QIcon(os.path.join(dirtools.DataFileDirs.Root, 'icon.png')))
    app.setStyleSheet(getBaseStyleSheet())
    return app


def launchApp(app, mainView, moduleMainControllers):
    """ Launches the app. The program will exit when the app is exited. """
    logger = initLogger('launchApp')
    #threading.Thread(target=embed_kernel, daemon=True).start()

    if IS_HEADLESS:
        """We won't have any GUI, so we don't need to prepare the app."""
        # Keep python running
        # embed_kernel() # TODO: This should be non-blocking!
        tDiskCheck = time.time()
        while True: # TODO: have webserver signal somehow?
            try:
                emit_queued()
                time.sleep(1)
                if time.time() - tDiskCheck > 60 and dirtools.getDiskusage() > 0.9:
                    # if the storage is full or the user presses Ctrl+C, we want to stop the experiment
                    moduleMainControllers.mapping["imcontrol"]._ImConMainController__commChannel.sigExperimentStop.emit()
                    tDiskCheck = time.time()

            except KeyboardInterrupt:
                exitCode = 0
                break

    else:
        # Show app
        if mainView is not None:
            mainView.showMaximized()
            mainView.show()
        exitCode = app.exec_()

    # Clean up
    for controller in moduleMainControllers:
        try:
            controller.closeEvent()
        except Exception:
            logger.error(f'Error closing {type(controller).__name__}')
            logger.error(traceback.format_exc())

    # Exit
    sys.exit(exitCode)


# Copyright (C) 2020-2024 ImSwitch developers
# This file is part of ImSwitch.
#
# ImSwitch is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ImSwitch is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
