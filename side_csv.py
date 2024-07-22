import sys
import pandas as pd
import matplotlib.pyplot as plt
from PySide6.QtWidgets import (QApplication, QMainWindow, QFileDialog, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QPushButton, QHBoxLayout, QLineEdit, QComboBox, QFormLayout, QDialog, QMessageBox)
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt

class CSVViewerEditorAnalyzer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.dataframe = pd.DataFrame()
        self.dark_mode_enabled = True
        self.applyDarkMode()

    def initUI(self):
        self.setWindowTitle('CSV Viewer, Editor, and Analyzer')
        self.setGeometry(100, 100, 1000, 600)

        self.tableWidget = QTableWidget()

        loadAction = QAction('Load CSV', self)
        loadAction.triggered.connect(self.loadCSV)

        saveAction = QAction('Save CSV', self)
        saveAction.triggered.connect(self.saveCSV)

        summaryAction = QAction('Summary Statistics', self)
        summaryAction.triggered.connect(self.showSummaryStatistics)

        filterAction = QAction('Filter Rows', self)
        filterAction.triggered.connect(self.filterRows)

        plotAction = QAction('Plot Data', self)
        plotAction.triggered.connect(self.plotData)

        toggleThemeAction = QAction('Toggle Dark Mode', self)
        toggleThemeAction.triggered.connect(self.toggleDarkMode)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('File')
        fileMenu.addAction(loadAction)
        fileMenu.addAction(saveAction)

        analyzeMenu = menubar.addMenu('Analyze')
        analyzeMenu.addAction(summaryAction)
        analyzeMenu.addAction(filterAction)
        analyzeMenu.addAction(plotAction)

        viewMenu = menubar.addMenu('View')
        viewMenu.addAction(toggleThemeAction)

        layout = QVBoxLayout()
        layout.addWidget(self.tableWidget)

        buttonLayout = QHBoxLayout()
        saveButton = QPushButton('Save CSV')
        saveButton.clicked.connect(self.saveCSV)
        buttonLayout.addWidget(saveButton)

        layout.addLayout(buttonLayout)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def loadCSV(self):
        filePath, _ = QFileDialog.getOpenFileName(self, 'Open CSV', '', 'CSV(*.csv)')
        if filePath == '':
            return

        self.dataframe = pd.read_csv(filePath)
        self.showDataInTable()

    def saveCSV(self):
        filePath, _ = QFileDialog.getSaveFileName(self, 'Save CSV', '', 'CSV(*.csv)')
        if filePath == '':
            return

        self.updateDataFrameFromTable()
        self.dataframe.to_csv(filePath, index=False)

    def showDataInTable(self):
        self.tableWidget.setRowCount(self.dataframe.shape[0])
        self.tableWidget.setColumnCount(self.dataframe.shape[1])
        self.tableWidget.setHorizontalHeaderLabels(self.dataframe.columns)

        for row in range(self.dataframe.shape[0]):
            for column in range(self.dataframe.shape[1]):
                self.tableWidget.setItem(row, column, QTableWidgetItem(str(self.dataframe.iat[row, column])))

    def updateDataFrameFromTable(self):
        for row in range(self.tableWidget.rowCount()):
            for column in range(self.tableWidget.columnCount()):
                item = self.tableWidget.item(row, column)
                self.dataframe.iat[row, column] = item.text() if item else ''

    def showSummaryStatistics(self):
        if self.dataframe.empty:
            QMessageBox.warning(self, 'Error', 'No data loaded')
            return

        summary = self.dataframe.describe()
        stats = summary.to_string()

        msgBox = QMessageBox()
        msgBox.setWindowTitle('Summary Statistics')
        msgBox.setText(stats)
        msgBox.exec()

    def filterRows(self):
        if self.dataframe.empty:
            QMessageBox.warning(self, 'Error', 'No data loaded')
            return

        dialog = FilterDialog(self.dataframe, self)
        dialog.exec()
        if dialog.result():
            self.dataframe = dialog.filtered_dataframe
            self.showDataInTable()

    def plotData(self):
        if self.dataframe.empty:
            QMessageBox.warning(self, 'Error', 'No data loaded')
            return

        dialog = PlotDialog(self.dataframe, self)
        dialog.exec()

    def toggleDarkMode(self):
        if self.dark_mode_enabled:
            self.setStyleSheet("")
        else:
            self.applyDarkMode()
        self.dark_mode_enabled = not self.dark_mode_enabled

    def applyDarkMode(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2e2e2e;
                color: #ffffff;
            }
            QTableWidget {
                background-color: #444444;
                color: #ffffff;
                gridline-color: #666666;
            }
            QHeaderView::section {
                background-color: #333333;
                color: #ffffff;
            }
            QMenuBar {
                background-color: #333333;
                color: #ffffff;
            }
            QMenu {
                background-color: #333333;
                color: #ffffff;
            }
            QAction {
                background-color: #333333;
                color: #ffffff;
            }
            QPushButton {
                background-color: #555555;
                color: #ffffff;
            }
        """)

class FilterDialog(QDialog):
    def __init__(self, dataframe, parent=None):
        super().__init__(parent)
        self.dataframe = dataframe
        self.filtered_dataframe = dataframe.copy()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Filter Rows')
        self.setGeometry(100, 100, 300, 200)

        layout = QVBoxLayout()
        formLayout = QFormLayout()

        self.columnComboBox = QComboBox()
        self.columnComboBox.addItems(self.dataframe.columns)
        formLayout.addRow('Column:', self.columnComboBox)

        self.filterLineEdit = QLineEdit()
        formLayout.addRow('Filter Value:', self.filterLineEdit)

        layout.addLayout(formLayout)

        buttonLayout = QHBoxLayout()
        filterButton = QPushButton('Apply Filter')
        filterButton.clicked.connect(self.applyFilter)
        buttonLayout.addWidget(filterButton)

        layout.addLayout(buttonLayout)

        self.setLayout(layout)

    def applyFilter(self):
        column = self.columnComboBox.currentText()
        value = self.filterLineEdit.text()

        self.filtered_dataframe = self.dataframe[self.dataframe[column].astype(str).str.contains(value)]
        self.accept()

class PlotDialog(QDialog):
    def __init__(self, dataframe, parent=None):
        super().__init__(parent)
        self.dataframe = dataframe
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Plot Data')
        self.setGeometry(100, 100, 400, 300)

        layout = QVBoxLayout()
        formLayout = QFormLayout()

        self.columnComboBox = QComboBox()
        self.columnComboBox.addItems(self.dataframe.columns)
        formLayout.addRow('Column:', self.columnComboBox)

        self.plotTypeComboBox = QComboBox()
        self.plotTypeComboBox.addItems(['Histogram', 'Scatter'])
        formLayout.addRow('Plot Type:', self.plotTypeComboBox)

        layout.addLayout(formLayout)

        buttonLayout = QHBoxLayout()
        plotButton = QPushButton('Plot')
        plotButton.clicked.connect(self.plot)
        buttonLayout.addWidget(plotButton)

        layout.addLayout(buttonLayout)

        self.setLayout(layout)

    def plot(self):
        column = self.columnComboBox.currentText()
        plot_type = self.plotTypeComboBox.currentText()

        try:
            if plot_type == 'Histogram':
                if not pd.api.types.is_numeric_dtype(self.dataframe[column]):
                    raise TypeError("No numeric data to plot")
                self.dataframe[column].plot(kind='hist')
            elif plot_type == 'Scatter':
                if len(self.dataframe.columns) < 2:
                    QMessageBox.warning(self, 'Error', 'Scatter plot requires at least two columns')
                    return
                y_column, ok = QFileDialog.getItem(self, 'Select Y Column', 'Select Y Column for Scatter Plot:', self.dataframe.columns.tolist())
                if not ok:
                    return
                if not pd.api.types.is_numeric_dtype(self.dataframe[column]) or not pd.api.types.is_numeric_dtype(self.dataframe[y_column]):
                    raise TypeError("No numeric data to plot")
                self.dataframe.plot(kind='scatter', x=column, y=y_column)

            plt.show()
            self.accept()
        except TypeError as e:
            QMessageBox.warning(self, 'Error', str(e))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWin = CSVViewerEditorAnalyzer()
    mainWin.show()
    sys.exit(app.exec())
