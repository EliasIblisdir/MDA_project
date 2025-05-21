from shiny import ui

app_ui = ui.page_fluid(
    ui.h2("CORDIS Horizon Europe Dashboard"),

    ui.navset_tab(
        ui.nav_panel(
            "Data Overview",
            ui.output_text_verbatim("data_summary")
        ),
        ui.nav_panel(
            "Funding Breakdown",
            ui.output_plot("plot_funding_vs_org")
            )
        )
    )

