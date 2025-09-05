# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'param_temp.ui'
##
## Created by: Qt User Interface Compiler version 6.8.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QDoubleSpinBox, QGridLayout, QHBoxLayout,
    QLabel, QSizePolicy, QWidget)

class Ui_Param_Temp(object):
    def setupUi(self, Param_Temp):
        if not Param_Temp.objectName():
            Param_Temp.setObjectName(u"Param_Temp")
        Param_Temp.resize(318, 95)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Param_Temp.sizePolicy().hasHeightForWidth())
        Param_Temp.setSizePolicy(sizePolicy)
        self.horizontalLayout = QHBoxLayout(Param_Temp)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(-1, 24, -1, -1)
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.offset_spinbox = QDoubleSpinBox(Param_Temp)
        self.offset_spinbox.setObjectName(u"offset_spinbox")
        self.offset_spinbox.setDecimals(6)
        self.offset_spinbox.setMinimum(-1000000000.000000000000000)
        self.offset_spinbox.setMaximum(1000000000.000000000000000)

        self.gridLayout.addWidget(self.offset_spinbox, 1, 1, 1, 1)

        self.label_5 = QLabel(Param_Temp)
        self.label_5.setObjectName(u"label_5")
        font = QFont()
        font.setBold(True)
        self.label_5.setFont(font)

        self.gridLayout.addWidget(self.label_5, 1, 0, 1, 1)

        self.label_9 = QLabel(Param_Temp)
        self.label_9.setObjectName(u"label_9")
        self.label_9.setFont(font)

        self.gridLayout.addWidget(self.label_9, 0, 0, 1, 1)

        self.scale_spinbox = QDoubleSpinBox(Param_Temp)
        self.scale_spinbox.setObjectName(u"scale_spinbox")
        self.scale_spinbox.setDecimals(9)
        self.scale_spinbox.setMinimum(-1000000000.000000000000000)
        self.scale_spinbox.setMaximum(1000000000.000000000000000)

        self.gridLayout.addWidget(self.scale_spinbox, 0, 1, 1, 1)

        self.gridLayout.setColumnStretch(0, 1)

        self.horizontalLayout.addLayout(self.gridLayout)

        QWidget.setTabOrder(self.scale_spinbox, self.offset_spinbox)

        self.retranslateUi(Param_Temp)

        QMetaObject.connectSlotsByName(Param_Temp)
    # setupUi

    def retranslateUi(self, Param_Temp):
        self.offset_spinbox.setSuffix(QCoreApplication.translate("Param_Temp", u" \u00b0C", None))
        self.label_5.setText(QCoreApplication.translate("Param_Temp", u"Offset", None))
        self.label_9.setText(QCoreApplication.translate("Param_Temp", u"Scale", None))
        self.scale_spinbox.setSuffix(QCoreApplication.translate("Param_Temp", u" \u00b0C/V", None))
        pass
    # retranslateUi

