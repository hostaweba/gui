import sys
import csv
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QFileDialog, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QPushButton, QHBoxLayout

class CSVViewerEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('CSV Viewer and Editor')
        self.setGeometry(100, 100, 800, 600)

        self.tableWidget = QTableWidget()
        
        loadAction = QAction('Load CSV', self)
        loadAction.triggered.connect(self.loadCSV)
        
        saveAction = QAction('Save CSV', self)
        saveAction.triggered.connect(self.saveCSV)
        
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('File')
        fileMenu.addAction(loadAction)
        fileMenu.addAction(saveAction)
        
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
        
        with open(filePath, newline='') as csvfile:
            reader = csv.reader(csvfile)
            data = list(reader)

        self.tableWidget.setRowCount(len(data))
        self.tableWidget.setColumnCount(len(data[0]))
        
        for row in range(len(data)):
            for column in range(len(data[row])):
                self.tableWidget.setItem(row, column, QTableWidgetItem(data[row][column]))

    def saveCSV(self):
        filePath, _ = QFileDialog.getSaveFileName(self, 'Save CSV', '', 'CSV(*.csv)')
        if filePath == '':
            return
        
        rowCount = self.tableWidget.rowCount()
        columnCount = self.tableWidget.columnCount()
        
        data = []
        for row in range(rowCount):
            rowData = []
            for column in range(columnCount):
                item = self.tableWidget.item(row, column)
                if item:
                    rowData.append(item.text())
                else:
                    rowData.append('')
            data.append(rowData)
        
        with open(filePath, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(data)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWin = CSVViewerEditor()
    mainWin.show()
    sys.exit(app.exec_())
