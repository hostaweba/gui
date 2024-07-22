import sys
import csv
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QFileDialog, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QPushButton, QHBoxLayout, QLabel, QLineEdit, QComboBox, QFormLayout, QDialog, QMessageBox

class CSVViewerEditorAnalyzer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.dataframe = pd.DataFrame()
        
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
        
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('File')
        fileMenu.addAction(loadAction)
        fileMenu.addAction(saveAction)
        
        analyzeMenu = menubar.addMenu('Analyze')
        analyzeMenu.addAction(summaryAction)
        analyzeMenu.addAction(filterAction)
        analyzeMenu.addAction(plotAction)
        
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
        msgBox.exec_()

    def filterRows(self):
        if self.dataframe.empty:
            QMessageBox.warning(self, 'Error', 'No data loaded')
            return
        
        dialog = FilterDialog(self.dataframe, self)
        dialog.exec_()
        if dialog.result():
            self.dataframe = dialog.filtered_dataframe
            self.showDataInTable()

    def plotData(self):
        if self.dataframe.empty:
            QMessageBox.warning(self, 'Error', 'No data loaded')
            return
        
        dialog = PlotDialog(self.dataframe, self)
        dialog.exec_()

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
        
        if plot_type == 'Histogram':
            self.dataframe[column].plot(kind='hist')
        elif plot_type == 'Scatter':
            if len(self.dataframe.columns) < 2:
                QMessageBox.warning(self, 'Error', 'Scatter plot requires at least two columns')
                return
            y_column, ok = QFileDialog.getItem(self, 'Select Y Column', 'Select Y Column for Scatter Plot:', self.dataframe.columns.tolist())
            if not ok:
                return
            self.dataframe.plot(kind='scatter', x=column, y=y_column)
        
        plt.show()
        self.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWin = CSVViewerEditorAnalyzer()
    mainWin.show()
    sys.exit(app.exec_())
