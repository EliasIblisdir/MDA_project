# app.py
from shiny import App, ui
from shinywidgets import output_widget, render_widget
import pandas as pd
import plotly.express as px




from sankey_diagram import build_sankey, df
from mda_distr_industries import sme_pie, industry_pie, choropleth_map_industries
from mda_distr_schemes import schemes_pie, choropleth_map_schemes




# Dummy Functions


# def build_sankey():
#     return px.pie(values=[1], names=["Sankey stub"], title="Sankey")

# def choropleth_map_industries():
#     return px.scatter_geo(title="Industry Map Stub")

# def choropleth_map_schemes():
#     return px.scatter_geo(title="Scheme Map Stub")

# def sme_pie(country):
#     return px.pie(values=[1, 2], names=["SME", "Non-SME"], title=f"SME Pie {country}")

# def industry_pie(country):
#     return px.pie(values=[2, 3], names=["A", "B"], title=f"Industry Pie {country}")

# def schemes_pie(country):
#     return px.pie(values=[1, 4], names=["Scheme 1", "Scheme 2"], title=f"Schemes Pie {country}")









app_ui = ui.page_fluid(

    ui.div(

        ui.navset_tab(
            
            # Tab 1: Sankey Diagram
            ui.nav_panel("Sankey Diagram",
                ui.h2("Horizon EU Sankey Diagram of Funding Flows (Top 10 Countries)"),
                ui.div(output_widget("sankey_plot"), style = "margin-top: 2em;")
            ),

            # Tab 2: Industry-based Distribution
            ui.nav_panel("Choropleth Map 1: Distribution of Funding across Sectors/Industries",
                # ui.h3("Gini Coefficient by Country"),
                # ui.h3("Mapping levels of Equitable Funding Distribution for Sectors/Industries/Research Areas across countries."),
                ui.input_select(
                "country_select_tab2",
                "Select a Country",
                choices=sorted(["AT", "BE", "BG", "CH", "CY", "CZ", "DE", "DK", "EE", "EL", "ES", 
                        "FI", "FR", "HR", "HU", "IE", "IS", "IT", "LI", "LT", "LU", "LV",
                        "MT", "NL", "NO", "PL", "PT", "RO", "SE", "SI", "SK", "TR", "UK"]),
                selected="DE"
                ),
                # Layout: Map + Pie charts
                ui.page_fluid(
                    output_widget("map1_plot"),
                    ui.layout_columns(
                        output_widget("industries"),
                        output_widget("sme_tab2")
                    )
                )
            ),

            # Tab 3: Scheme-based Distribution
            ui.nav_panel("Choropleth Map 2: Distribution of Funding across Funding Schemes",
                # ui.h3("Gini Coefficient by Country"),
                # ui.h3("Mapping levels of Equitable Funding Distribution for Funding Schemes, across Countries."),
                ui.input_select(
                "country_select_tab3",
                "Select a Country",
                choices=sorted(["AT", "BE", "BG", "CH", "CY", "CZ", "DE", "DK", "EE", "EL", "ES", 
                        "FI", "FR", "HR", "HU", "IE", "IS", "IT", "LI", "LT", "LU", "LV",
                        "MT", "NL", "NO", "PL", "PT", "RO", "SE", "SI", "SK", "TR", "UK"]),
                selected="DE"
                ),
                
                # Layout: Map + Pie charts
                ui.page_fluid(
                    output_widget("map2_plot"),
                    ui.layout_columns(
                        output_widget("schemes"),
                        output_widget("sme_tab3")  # reused here too
                    )
                )
            )
        ),
        style="background-color: #FFFBF0; min-height: 100vh; padding: 1em;"
    )
)


 
    




def server(input, output, session):
    @output
    @render_widget
    
    def sankey_plot():
        print("Rendering sankey...")
        return build_sankey(df)

    @output
    @render_widget
    def map1_plot():
        print("Rendering map1...")
        return choropleth_map_industries()

    @output
    @render_widget
    def map2_plot():
        print("Rendering map2...")
        return choropleth_map_schemes()

    @output
    @render_widget
    def sme_tab2():
        print("Rendering SME tab 2...")
        return sme_pie(input["country_select_tab2"]())

    @output
    @render_widget
    def sme_tab3():
        print("Rendering SME tab 3...")
        return sme_pie(input["country_select_tab3"]())

    @output
    @render_widget
    def industries():
        print("Rendering industry pie...")
        return industry_pie(input["country_select_tab2"]())

    @output
    @render_widget
    def schemes():
        print("Rendering scheme pie...")
        return schemes_pie(input["country_select_tab3"]())

     

app = App(app_ui, server)
