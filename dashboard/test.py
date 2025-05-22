import shiny
from shiny import App, ui , render 
import matplotlib.pyplot as plt
import numpy as np

app_ui = ui.page_fluid(
                    ui.input_numeric("n", "Sample size", 25), 
                    ui.output_plot("hist")
                    )

def server (input , output , session ): 
    @render.plot
    def hist ():
        n = input.n()
        data = np.random.randn(n)
        fig, ax=plt.subplots()
        ax.hist(data, bins=10, edgecolor="black")
        return fig

app=App(app_ui, server)