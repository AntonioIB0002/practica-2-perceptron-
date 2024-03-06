import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QMessageBox, QFileDialog
from PyQt5.QtGui import QPen,QColor
from PyQt5.QtCore import Qt, QLineF, QTimer
from mw import Ui_MainWindow
import numpy as np
import random

class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.scene = QGraphicsScene(self)
        self.scene.setSceneRect(0, 0, 740, 740)

        self.line_item = None
        self.coordenadas = []
        self.salidas_deseadas = []
        self.error = []
        self.limite_de_epocas = 0
        self.factor_de_aprendizaje = 0
        self.w1 = round(random.uniform(0, 1), 5)
        self.w2 = round(random.uniform(0, 1), 5)
        self.bias = round(random.uniform(0, 1), 5)
        self.Cartesiano()
        self.ui.pushButton_graficar.clicked.connect(self.grafica)
        self.ui.pushButton_reset.clicked.connect(self.reset)
        self.ui.pushButton_exportar.clicked.connect(self.AbrirArchivo)
        self.ui.pushButton.clicked.connect(self.Archivo_Salidas)
        self.contador = 0

    def AbrirArchivo(self):
        archivo, _ = QFileDialog.getOpenFileName(None, "Seleccionar archivo", "", "Archivos de texto (*.txt)")
        try:
            with open(archivo, 'r') as f:
                for linea in f:
                    x, y = map(float, linea.strip().split(','))
                    # Ajuste de coordenadas
                    self.coordenadas.append((x, y))
                    # Se agrega el punto a la escena gráfica
                    pen = QPen(Qt.red)
                    brush = Qt.red
                    self.scene.addEllipse(x * 20 + self.scene.width() / 2 - 2, -y * 20 + self.scene.height() / 2 - 2, 4, 4, pen, brush)

        except Exception as e:
            QMessageBox.warning(self, 'Error', 'Archivo no válido')

    def Archivo_Salidas(self):
        archivo, _ = QFileDialog.getOpenFileName(None, "Seleccionar archivo", "", "Archivos de texto (*.txt)")
        try:
            with open(archivo, 'r') as f:
                for linea in f:
                    linea = linea.strip()
                    self.salidas_deseadas.append(float(linea))

        except Exception as e:
            QMessageBox.warning(self, 'Error', 'Archivo no válido')

    def precision(self, y_true, y_pred):
        true_positives = np.sum(np.logical_and(y_true == 1, y_pred == 1))
        false_positives = np.sum(np.logical_and(y_true == -1, y_pred == 1))
        return true_positives / (true_positives + false_positives)

    def confusion_matrix(self, y_true, y_pred):
        tp = np.sum(np.logical_and(y_true == 1, y_pred == 1))
        fp = np.sum(np.logical_and(y_true == -1, y_pred == 1))
        tn = np.sum(np.logical_and(y_true == -1, y_pred == -1))
        fn = np.sum(np.logical_and(y_true == 1, y_pred == -1))
        return np.array([[tp, fp], [fn, tn]])

    def f1_score(self, y_true, y_pred):
        precision_val = self.precision(y_true, y_pred)
        recall = self.precision(y_pred, y_true)
        return 2 * (precision_val * recall) / (precision_val + recall)

    def perseptron(self):
        if self.limite_de_epocas > 0:
            x1 = 0
            x2 = 0
            y_true = []  # Lista para almacenar las etiquetas verdaderas
            y_pred = []  # Lista para almacenar las etiquetas predichas

            for i in range(len(self.coordenadas)):
                x1 = self.coordenadas[i][0]
                x2 = self.coordenadas[i][1]
                y = self.w1 * x1 + x2 * self.w2 + self.bias
                if y >= 0:
                    y = 1
                else:
                    y = 0
                e = self.salidas_deseadas[i] - y
                self.error.append(e)

                # Almacenar las etiquetas verdaderas y predichas
                y_true.append(self.salidas_deseadas[i])
                y_pred.append(y)

                if y == 0:
                    self.scene.addEllipse((self.coordenadas[i][0]) * 20 + self.scene.width() / 2 - 2,
                                        -(self.coordenadas[i][1]) * 20 + self.scene.height() / 2 - 2, 4, 4,
                                        QPen(Qt.red), Qt.red)
                else:
                    self.scene.addEllipse((self.coordenadas[i][0]) * 20 + self.scene.width() / 2 - 2,
                                        -(self.coordenadas[i][1]) * 20 + self.scene.height() / 2 - 2, 4, 4,
                                        QPen(Qt.blue), Qt.blue)

                if e != 0:
                    self.w1 = round((self.w1 + self.factor_de_aprendizaje * e * x1), 5)
                    self.w2 = round((self.w2 + self.factor_de_aprendizaje * e * x2), 5)
                    self.bias = round((self.bias + self.factor_de_aprendizaje * e), 5)

            # Calcular precisión, matriz de confusión y f1_score
            precision_value = self.precision(np.array(y_true), np.array(y_pred))
            conf_matrix = self.confusion_matrix(np.array(y_true), np.array(y_pred))
            f1score = self.f1_score(np.array(y_true), np.array(y_pred))

            print("Precisión:", precision_value)
            print("Matriz de Confusión:")
            print(conf_matrix)
            print("F1 Score:", f1score)

            self.contador += 1

            m = -self.w1 / self.w2
            c = -self.bias / self.w2

            x1 = -20
            y1 = m * x1 + c
            x2 = 20
            y2 = m * x2 + c

            # AJuste para cuadrar en el plano
            y1 = -y1 * 20 + self.scene.height() / 2
            y2 = -y2 * 20 + self.scene.height() / 2
            x1 = x1 * 20 + self.scene.width() / 2
            x2 = x2 * 20 + self.scene.width() / 2

            if self.line_item is not None:
                self.scene.removeItem(self.line_item)
            line = QLineF(x1, y1, x2, y2)
            pen = QPen(Qt.green)
            pen.setWidth(2)
            self.line_item = self.scene.addLine(line, pen)
            self.ui.lineEdit_w1.setText(str(self.w1))
            self.ui.lineEdit_w2.setText(str(self.w2))
            self.ui.lineEdit_bias.setText(str(self.bias))

            self.limite_de_epocas -= 1

            if all(elementos == 0 for elementos in self.error):
                self.graph_timer.stop()

            self.error.clear()
        else:
            self.graph_timer.stop()

    def reset(self):
        self.scene.clear()
        self.coordenadas.clear()
        self.Cartesiano()
        self.salidas_deseadas.clear()
        self.w1 = round(random.uniform(0, 1), 5)
        self.w2 = round(random.uniform(0, 1), 5)
        self.bias = round(random.uniform(0, 1), 5)
        self.ui.lineEdit_bias.setText(str(self.bias))
        self.ui.lineEdit_w1.setText(str(self.w1))
        self.ui.lineEdit_w2.setText(str(self.w2))
        self.error.clear()

    def grafica(self):
        if self.validacion():
            self.graph_timer = QTimer(self)
            self.graph_timer.timeout.connect(self.perseptron)
            self.graph_timer.start(2000)

    def validacion(self):
        try:
            self.factor_de_aprendizaje = float(self.ui.lineEdit_factor.text())
            self.limite_de_epocas = float(self.ui.lineEdit_limite.text())
            if self.limite_de_epocas < 0:
                QMessageBox.warning(self, 'Captura no válida', 'Ingrese solo números enteros o reales positivos.')
                return False
            if len(self.coordenadas) == 0:
                QMessageBox.warning(self, 'Ingrese entradas', 'Seleccione entradas en el plano')
                return False
            return True
        except ValueError:
            QMessageBox.warning(self, 'Captura no válida', 'Ingrese solo números enteros o reales positivos.')
            return False

    def Cartesiano(self):
        gris = QColor(238, 223, 220)
        for x in range(-20, 21):
            self.scene.addLine(self.scene.width() / 2 + x * 20, 0, self.scene.width() / 2 + x * 20, self.scene.height(),
                               gris)
            self.scene.addLine(self.scene.width() / 2 + x * 20, self.scene.height() / 2 - 5,
                               self.scene.width() / 2 + x * 20, self.scene.height() / 2 + 5, Qt.black)

        for y in range(-20, 21):
            self.scene.addLine(0, self.scene.height() / 2 + y * 20, self.scene.width(),
                               self.scene.height() / 2 + y * 20, gris)
            self.scene.addLine(self.scene.width() / 2 - 5, self.scene.height() / 2 + y * 20,
                               self.scene.width() / 2 + 5, self.scene.height() / 2 + y * 20, Qt.black)

        self.scene.addLine(0, self.scene.height() / 2, self.scene.width(), self.scene.height() / 2, Qt.black)
        self.scene.addLine(self.scene.width() / 2, 0, self.scene.width() / 2, self.scene.height())

        self.ui.graphicsView.setScene(self.scene)

        self.ui.lineEdit_bias.setText(str(self.bias))
        self.ui.lineEdit_w1.setText(str(self.w1))
        self.ui.lineEdit_w2.setText(str(self.w2))

app = QApplication(sys.argv)
ventana = Window()
ventana.show()
sys.exit(app.exec_())
