from shiny import render
from shinywidgets import render_plotly
import plotly.express as px
import pandas as pd
import os

DATA = os.path.join(os.path.dirname(__file__), "..", "Data")
project_financials = pd.read_pickle(os.path.join(DATA, "finance.pkl"))

projects = pd.read_pickle(os.path.join(DATA, "projects.pkl"))
organizations = pd.read_pickle(os.path.join(DATA, "organizations.pkl"))
deliverables = pd.read_pickle(os.path.join(DATA, "deliverables.pkl"))
publications = pd.read_pickle(os.path.join(DATA, "publications.pkl"))
reports = pd.read_pickle(os.path.join(DATA,"reports.pkl"))
data = pd.read_pickle(os.path.join(DATA,"PE.pkl"))

def server(input, output, session):


    @output
    @render.text
    def data_summary():
        return (
            df_info(data, "Main") + 
            df_info(projects, "Projects") +
            df_info(organizations, "Organizations") +
            df_info(deliverables, "Deliverables") +
            df_info(publications, "Publications") +
            df_info(reports, "Reports")
        )

    # Helper function to get info
    def df_info(df, name):
        return (
            f"📄 {name}\n"
            f"Rows: {len(df)}\n"
            f"Columns: {', '.join(df.columns)}\n\n"
        )

    @output
    @render_plotly
    def plot_funding_vs_org():
        df = pd.DataFrame({
                "x": [1, 2, 3],
                "y": [10, 20, 15]
            })

        fig = px.line(df, x="x", y="y", title="Minimal Test Plot")
        return fig

