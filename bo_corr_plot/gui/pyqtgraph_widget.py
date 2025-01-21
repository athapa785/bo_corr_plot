# bo_corr_plot/gui/pyqtgraph_widget.py
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
import numpy as np
import torch
from botorch.acquisition.analytic import ExpectedImprovement, UpperConfidenceBound


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
        self.top_plot.addLegend(offset=(10,10))

        self.layout_widget.nextRow()

        # Bottom plot
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
        self.bottom_plot.addLegend(offset=(10,10))

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

    def update_plot_botorch(self, model, X_np, X_torch, X_samples, Y_samples,
                            iteration, acquisition_function, exploration_param):
        """
        Update the top/bottom plots using the BoTorch model's posterior
        and built-in acquisition functions (EI or UCB).
        """
        self.clear_plots()

        # Convert to torch
        model.eval()
        with torch.no_grad():
            posterior = model(X_torch)  # shape: (N_eval, 1)
            mean = posterior.mean.view(-1).detach().numpy()
            std = posterior.variance.sqrt().view(-1).detach().numpy()

        # Sort by X for nice plotting
        sort_idx = np.argsort(X_np.flatten())
        X_sorted = X_np.flatten()[sort_idx]
        mean_sorted = mean[sort_idx]
        std_sorted = std[sort_idx]

        upper = mean_sorted + 1.96 * std_sorted
        lower = mean_sorted - 1.96 * std_sorted

        # Best sample
        best_idx = Y_samples.argmax()
        best_x = X_samples[best_idx][0]
        best_y = Y_samples[best_idx][0]

        # Build an acquisition function instance for the bottom plot
        if acquisition_function == "ei":
            best_f = float(Y_samples.max())
            acq_fn = ExpectedImprovement(model, best_f=best_f)
            label_str = f"EI (best_f={best_f:.3f}, xi~0)"
        else:
            acq_fn = UpperConfidenceBound(model, beta=exploration_param)
            label_str = f"UCB (beta={exploration_param:.3f})"

        # Fix shape of X_torch for the acquisition function
        with torch.no_grad():
            acq_values = acq_fn(X_torch.unsqueeze(-2)).view(-1).detach().numpy()
        acq_values_sorted = acq_values[sort_idx]

        self.top_plot.setTitle(f"Iteration {iteration}: BoTorch GP + Samples", color='w')

        # Plot mean
        gp_line = self.top_plot.plot(
            X_sorted, mean_sorted, 
            pen=pg.mkPen('w', width=2),
            name='GP Mean'
        )

        # Confidence interval
        transparent_pen = pg.mkPen(color=(0,0,0,0))
        upper_curve = self.top_plot.plot(X_sorted, upper, pen=transparent_pen)
        lower_curve = self.top_plot.plot(X_sorted, lower, pen=transparent_pen)
        fill_brush = (0,191,255,100)
        fill = pg.FillBetweenItem(upper_curve, lower_curve, brush=fill_brush)
        self.top_plot.addItem(fill)

        # Samples
        self.top_plot.plot(
            X_samples.flatten(),
            Y_samples.flatten(),
            pen=None, symbol='o', symbolPen=None,
            symbolSize=6, symbolBrush='r',
            name='Samples'
        )

        # Best sample
        self.top_plot.plot(
            [best_x], [best_y],
            pen=None, symbol='star', symbolSize=10, symbolBrush='g',
            name='Best Sample'
        )

        # Plot the acquisition
        self.bottom_plot.plot(
            X_sorted, acq_values_sorted,
            pen=pg.mkPen('lime', width=2),
            name=label_str
        )

        # Auto-range
        self.top_plot.enableAutoRange('xy', True)
        self.bottom_plot.enableAutoRange('xy', True)