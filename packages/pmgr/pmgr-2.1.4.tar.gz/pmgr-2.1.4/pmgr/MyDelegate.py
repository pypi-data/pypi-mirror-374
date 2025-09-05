import re

import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt

#########################################################################
#
# Code shamelessly stolen from http://jdreaver.com/posts/2014-07-28-scientific-notation-spin-box-pyside.html.
#

_float_re = re.compile(r"(([+-]?\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?)")


def valid_float_string(string):
    match = _float_re.search(string)
    return match.groups()[0] == string if match else False


class FloatValidator(QtGui.QValidator):
    def validate(self, string, position):
        if valid_float_string(string):
            return (self.State.Acceptable, string, position)
        s = str(string)
        if s == "" or s[position - 1] in "e.-+":
            return (self.State.Intermediate, string, position)
        return (self.State.Invalid, string, position)

    def fixup(self, text):
        match = _float_re.search(str(text))
        return match.groups()[0] if match else ""


class ScientificDoubleSpinBox(QtWidgets.QDoubleSpinBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimum(-np.inf)
        self.setMaximum(np.inf)
        self.validator = FloatValidator()
        self.setDecimals(1000)

    def validate(self, text, position):
        return self.validator.validate(text, position)

    def fixup(self, text):
        return self.validator.fixup(text)

    def valueFromText(self, text):
        return float(text)

    def textFromValue(self, value):
        return format_float(value)

    def stepBy(self, steps):
        text = self.cleanText()
        groups = _float_re.search(text).groups()
        decimal = float(groups[1])
        decimal += steps
        new_string = f"{decimal:g}" + (groups[3] if groups[3] else "")
        self.lineEdit().setText(new_string)


def format_float(value):
    """Modified form of the 'g' format specifier."""
    string = f"{value:g}".replace("e+", "e")
    string = re.sub(r"e(-?)0*(\d+)", r"e\1\2", string)
    return string


#########################################################################


class MyDelegate(QtWidgets.QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        e = index.model().editorInfo(index)
        if e == str:
            editor = QtWidgets.QItemEditorFactory.defaultFactory().createEditor(
                QtCore.QVariant.String, parent
            )
            editor.mydelegate = False
        elif e == int:
            editor = QtWidgets.QItemEditorFactory.defaultFactory().createEditor(
                QtCore.QVariant.Int, parent
            )
            editor.mydelegate = False
        elif e == float:
            editor = ScientificDoubleSpinBox(parent)
            editor.mydelegate = False
        else:
            # Must be an enum list!
            editor = QtWidgets.QComboBox(parent)
            editor.enum = e
            editor.setAutoFillBackground(True)
            for item in e:
                editor.addItem(item)
            editor.mydelegate = True
        return editor

    def setEditorData(self, editor, index):
        if editor.mydelegate:
            value = index.model().data(index, Qt.EditRole)
            try:
                idx = editor.enum.index(value)
                editor.setCurrentIndex(idx)
            except Exception:
                # What was dumb is now smart?!?
                editor.setCurrentIndex(0)
        else:
            super().setEditorData(editor, index)

    def setModelData(self, editor, model, index):
        if editor.mydelegate:
            if editor.enum is None:
                v = editor.checkState()
                if v == Qt.Checked:
                    model.setData(index, 1)
                else:
                    model.setData(index, 0)
            else:
                model.setData(index, editor.currentText())
        else:
            super().setModelData(editor, model, index)
