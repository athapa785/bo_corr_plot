import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout)
import numpy as np
from ..core.acquisition import expected_improvement, upper_confidence_bound
from ..data.mock_data import objective_function

class PyQtGraphWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        main_layout = QHBoxLayout()
        self.setLayout(main_layout)

        plot_layout = QVBoxLayout()
        main_layout.addLayout(plot_layout, 1)

        self.layout_widget = pg.GraphicsLayoutWidget()
        self.layout_widget.setBackground((0,15,25))  # Dark background for qdarkstyle
        plot_layout.addWidget(self.layout_widget)

        # Top plot
        self.top_plot = self.layout_widget.addPlot(row=0, col=0, title="GP Prediction and Samples")
        self.top_plot.showGrid(x=True, y=True)
        self.top_plot.setTitle("GP Prediction and Samples", color='w')
        self.top_plot.getAxis('left').setPen('w')
        self.top_plot.getAxis('left').setTextPen('w')
        self.top_plot.getAxis('bottom').setPen('w')
        self.top_plot.getAxis('bottom').setTextPen('w')
        self.top_plot.getAxis('left').setLabel('f(X)', color='w')
        self.top_plot.enableAutoRange('xy', True)
        self.top_plot.addLegend(offset=(10,10))  # Add legend on top plot

        self.layout_widget.nextRow()

        # Bottom plot (Acquisition)
        self.bottom_plot = self.layout_widget.addPlot(row=1, col=0, title="Acquisition Function")
        self.bottom_plot.showGrid(x=True, y=True)
        self.bottom_plot.setTitle("Acquisition Function", color='w')
        self.bottom_plot.getAxis('left').setPen('w')
        self.bottom_plot.getAxis('left').setTextPen('w')
        self.bottom_plot.getAxis('bottom').setPen('w')
        self.bottom_plot.getAxis('bottom').setTextPen('w')
        self.bottom_plot.getAxis('left').setLabel('Acquisition', color='w')
        self.bottom_plot.getAxis('bottom').setLabel('X', color='w')
        self.bottom_plot.enableAutoRange('xy', True)
        self.bottom_plot.addLegend(offset=(10,10))  # Add legend on bottom plot

        # Crosshair lines
        self.vLine = pg.InfiniteLine(angle=90, movable=False, pen=pg.mkPen('w', style=QtCore.Qt.DashLine))
        self.hLine = pg.InfiniteLine(angle=0, movable=False, pen=pg.mkPen('w', style=QtCore.Qt.DashLine))
        self.top_plot.addItem(self.vLine, ignoreBounds=True)
        self.top_plot.addItem(self.hLine, ignoreBounds=True)

        self.proxy = pg.SignalProxy(self.top_plot.scene().sigMouseMoved, rateLimit=60, slot=self.mouseMoved)

    def mouseMoved(self, evt):
        pos = evt[0]
        if self.top_plot.sceneBoundingRect().contains(pos):
            mousePoint = self.top_plot.vb.mapSceneToView(pos)
            self.vLine.setPos(mousePoint.x())
            self.hLine.setPos(mousePoint.y())

    def clear_plots(self):
        self.top_plot.clear()
        self.bottom_plot.clear()
        # Re-add crosshair lines after clear
        self.top_plot.addItem(self.vLine, ignoreBounds=True)
        self.top_plot.addItem(self.hLine, ignoreBounds=True)

    def update_plot(self, gpr, X, X_samples, Y_samples, iteration, acquisition_function, exploration_param):
        self.clear_plots()

        sort_idx = np.argsort(X.flatten())
        X_sorted = X.flatten()[sort_idx]

        Y_pred, sigma = gpr.predict(X, return_std=True)
        Y_pred = Y_pred[sort_idx]
        sigma = sigma[sort_idx]

        upper = Y_pred + 1.96*sigma
        lower = Y_pred - 1.96*sigma

        # Best sample
        best_idx = Y_samples.argmax()
        best_x = X_samples[best_idx][0]
        best_y = Y_samples[best_idx][0]

        # Acquisition
        if acquisition_function == 'ei':
            acq = expected_improvement(X, X_samples, Y_samples, gpr, xi=exploration_param)
            acq_label = f'EI (xi={exploration_param:.2f})'
        else:
            acq = upper_confidence_bound(X, X_samples, Y_samples, gpr, kappa=exploration_param)
            acq_label = f'UCB (kappa={exploration_param:.2f})'

        acq = acq[sort_idx]

        self.top_plot.setTitle(f"Iteration {iteration}: Gaussian Process Regression and Samples", color='w')

        # Plot GP prediction with a name
        gp_line = self.top_plot.plot(X_sorted, Y_pred, pen=pg.mkPen('w', width=2), name='GP Prediction')

        # Confidence interval
        transparent_pen = pg.mkPen(color=(0,0,0,0))
        upper_curve = self.top_plot.plot(X_sorted, upper, pen=transparent_pen)
        lower_curve = self.top_plot.plot(X_sorted, lower, pen=transparent_pen)

        fill_brush = (0,191,255,100)
        fill = pg.FillBetweenItem(upper_curve, lower_curve, brush=fill_brush)
        self.top_plot.addItem(fill)

        # Samples
        self.top_plot.plot(X_samples.flatten(), Y_samples.flatten(), pen=None, symbol='o', symbolPen=None,
                           symbolSize=6, symbolBrush='r', name='Samples')

        # Best sample
        self.top_plot.plot([best_x], [best_y], pen=None, symbol='star', symbolSize=10, symbolBrush='g', name='Best Sample')

        # Acquisition
        self.bottom_plot.plot(X_sorted, acq, pen=pg.mkPen('lime', width=2), name=acq_label)

        # Auto-range
        self.top_plot.enableAutoRange('xy', True)
        self.bottom_plot.enableAutoRange('xy', True)