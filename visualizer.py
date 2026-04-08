"""Визуализация результатов бэктеста."""
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

class BacktestVisualizer:
    @staticmethod
    def plot_equity(equity_curve: list, parent=None) -> FigureCanvas:
        fig, ax = plt.subplots(figsize=(8, 4))
        fig.patch.set_facecolor('#111111')
        ax.set_facecolor('#000000')
        ax.plot(equity_curve, color='#ffd700', linewidth=2)
        ax.set_title("Equity Curve", color='white')
        ax.tick_params(colors='white')
        for spine in ax.spines.values(): spine.set_color('#333333')
        
        canvas = FigureCanvas(fig)
        return canvas
