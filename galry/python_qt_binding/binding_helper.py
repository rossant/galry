#!/usr/bin/env python

# Copyright (c) 2011, Dirk Thomas, Dorian Scholz, TU Darmstadt
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#   * Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#   * Redistributions in binary form must reproduce the above
#     copyright notice, this list of conditions and the following
#     disclaimer in the documentation and/or other materials provided
#     with the distribution.
#   * Neither the name of the TU Darmstadt nor the names of its
#     contributors may be used to endorse or promote products derived
#     from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import os
import sys
import __builtin__
from ..debugtools import log_debug, log_info, log_warn

def _select_qt_binding(binding_name=None):
    global QT_BINDING, QT_BINDING_VERSION

    # order of default bindings can be changed here
    # DEFAULT_BINDING_ORDER = ['pyside', 'pyqt']  # PySide first
    DEFAULT_BINDING_ORDER = ['pyqt', 'pyside']  # PyQt first

    # determine binding preference
    if binding_name is not None:
        if binding_name not in DEFAULT_BINDING_ORDER:
            raise ImportError('Qt binding "%s" is unknown' % binding_name)
        DEFAULT_BINDING_ORDER = [binding_name]

    required_modules = [
        'QtCore',
        'QtGui'
    ]
    optional_modules = [
        'QtDeclarative',
        'QtMultimedia',
        'QtNetwork',
        'QtOpenGL',
        'QtOpenVG',
        'QtScript',
        'QtScriptTools'
        'QtSql',
        'QtSvg',
        'QtWebKit',
        'QtXml',
        'QtXmlPatterns',
    ]

    # try to load preferred bindings
    error_msgs = []
    for binding_name in DEFAULT_BINDING_ORDER:
        try:
            binding_loader = getattr(sys.modules[__name__], '_load_%s' % binding_name, None)
            if binding_loader is not None:
                QT_BINDING_VERSION = binding_loader(required_modules, optional_modules)
                QT_BINDING = binding_name
                break
            else:
                error_msgs.append('  Binding loader "_load_%s" not found.' % binding_name)
        except ImportError, e:
            error_msgs.append('  ImportError for "%s": %s' % (binding_name, e))

    if QT_BINDING is None:
        raise ImportError('Could not find Qt binding (looked for "%s"):\n%s' % (DEFAULT_BINDING_ORDER, '\n'.join(error_msgs)))


def _register_binding_module(module_name, module):
    # register module using only its own name (TODO: legacy compatibility, remove when possible)
    sys.modules[module_name] = module
    # add module to the binding modules
    QT_BINDING_MODULES[module_name] = module


def _named_import(name):
    parts = name.split('.')
    assert(len(parts) >= 2)
    module = __builtin__.__import__(name)
    for m in parts[1:]:
        module = module.__dict__[m]
    module_name = parts[-1]
    _register_binding_module(module_name, module)


def _named_optional_import(name):
    try:
        _named_import(name)
    except ImportError:
        pass


def _load_pyqt(required_modules, optional_modules):
    
    # set environment variable QT_API for matplotlib
    os.environ['QT_API'] = 'pyqt'

    # select PyQt4 API, see http://www.riverbankcomputing.co.uk/static/Docs/PyQt4/html/incompatible_apis.html
    import sip
    try:
        sip.setapi('QDate', 2)
        sip.setapi('QDateTime', 2)
        sip.setapi('QString', 2)
        sip.setapi('QTextStream', 2)
        sip.setapi('QTime', 2)
        sip.setapi('QUrl', 2)
        sip.setapi('QVariant', 2)
    except ValueError, e:
        raise RuntimeError('Could not set API version (%s): did you import PyQt4 directly?' % e)

    # register required and optional PyQt4 modules
    for module_name in required_modules:
        _named_import('PyQt4.%s' % module_name)
    for module_name in optional_modules:
        _named_optional_import('PyQt4.%s' % module_name)

    # set some names for compatibility with PySide
    sys.modules['QtCore'].Signal = sys.modules['QtCore'].pyqtSignal
    sys.modules['QtCore'].Slot = sys.modules['QtCore'].pyqtSlot
    sys.modules['QtCore'].Property = sys.modules['QtCore'].pyqtProperty

    # try to register PyQt4.Qwt5 module
    try:
        import PyQt4.Qwt5
        _register_binding_module('Qwt', PyQt4.Qwt5)
    except ImportError:
        pass

    global loadUi

    def loadUi(uifile, baseinstance=None, custom_widgets=None):
        from PyQt4 import uic
        return uic.loadUi(uifile, baseinstance=baseinstance)

    # override specific function to improve compatibility between different bindings
    from QtGui import QFileDialog
    QFileDialog.getOpenFileName = QFileDialog.getOpenFileNameAndFilter
    QFileDialog.getSaveFileName = QFileDialog.getSaveFileNameAndFilter

    import PyQt4.QtCore
    
    log_info("PyQt loaded")
    
    return PyQt4.QtCore.PYQT_VERSION_STR


def _load_pyside(required_modules, optional_modules):
    
    # set environment variable QT_API for matplotlib
    os.environ['QT_API'] = 'pyside'

    # register required and optional PySide modules
    for module_name in required_modules:
        _named_import('PySide.%s' % module_name)
    for module_name in optional_modules:
        _named_optional_import('PySide.%s' % module_name)

    # set some names for compatibility with PyQt4
    sys.modules['QtCore'].pyqtSignal = sys.modules['QtCore'].Signal
    sys.modules['QtCore'].pyqtSlot = sys.modules['QtCore'].Slot
    sys.modules['QtCore'].pyqtProperty = sys.modules['QtCore'].Property

    # try to register PySideQwt module
    try:
        import PySideQwt
        _register_binding_module('Qwt', PySideQwt)
    except ImportError:
        pass

    global loadUi

    def loadUi(uifile, baseinstance=None, custom_widgets=None):
        from PySide.QtUiTools import QUiLoader
        from PySide.QtCore import QMetaObject

        class CustomUiLoader(QUiLoader):
            class_aliases = {
                'Line': 'QFrame',
            }

            def __init__(self, baseinstance=None, custom_widgets=None):
                super(CustomUiLoader, self).__init__(baseinstance)
                self._base_instance = baseinstance
                self._custom_widgets = custom_widgets or {}

            def createWidget(self, class_name, parent=None, name=''):
                # don't create the top-level widget, if a base instance is set
                if self._base_instance is not None and parent is None:
                    return self._base_instance

                if class_name in self._custom_widgets:
                    widget = self._custom_widgets[class_name](parent)
                else:
                    widget = QUiLoader.createWidget(self, class_name, parent, name)

                if str(type(widget)).find(self.class_aliases.get(class_name, class_name)) < 0:
                    sys.modules['QtCore'].qDebug(str('PySide.loadUi(): could not find widget class "%s", defaulting to "%s"' % (class_name, type(widget))))

                if self._base_instance is not None:
                    setattr(self._base_instance, name, widget)

                return widget

        loader = CustomUiLoader(baseinstance, custom_widgets)

        # instead of passing the custom widgets, they should be registered using QUiLoader.registerCustomWidget(),
        # but this does not work in PySide 1.0.6: it simply segfaults...
        #loader = CustomUiLoader(baseinstance)
        #custom_widgets = custom_widgets or {}
        #for custom_widget in custom_widgets.values():
        #    loader.registerCustomWidget(custom_widget)

        ui = loader.load(uifile)
        QMetaObject.connectSlotsByName(ui)
        return ui

    import PySide
    
    log_info("PySide loaded")
    
    return PySide.__version__


QT_BINDING = None
QT_BINDING_MODULES = {}
QT_BINDING_VERSION = None

_select_qt_binding(getattr(sys, 'SELECT_QT_BINDING', None))
