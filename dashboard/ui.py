from shiny import ui
from shinywidgets import output_widget


description = """
### Funding Breakdown Panel

This section explores how reported financial values compare between two levels of the Horizon Europe dataset:

#### Project-level data
| Column               | Meaning |
|----------------------|---------|
| `totalCost`          | The full cost of the project (across all funding sources — EU + others) |
| `ecMaxContribution`  | The maximum EU funding allocated to the project |

This implies:
- `ecMaxContribution ≤ totalCost`

#### Organization-level data
| Column               | Meaning |
|----------------------|---------|
| `ecContribution`     | EU contribution allocated to that organization (may include funds for third parties) |
| `netEcContribution`  | Actual EU money retained by the organization (after transfers) |
| `totalCost`          | Total cost incurred by the organization (EU-funded or otherwise) |

We expect:
- `Σ ecContribution ≈ ecMaxContribution`
- `Σ totalCost (orgs) ≈ totalCost (project)`
- `ecContribution ≥ netEcContribution`
"""


app_ui = ui.page_fluid(
    ui.h2("Horizon Europe – Dashboard"),

    ui.navset_tab(
        ui.nav_panel(
            "Data Table",
            ui.output_data_frame("data_preview")
        ),

    ui.nav_panel(
        "Funding Breakdown",

        ui.markdown(description),

        output_widget("plot_ec_scatter"),
        ui.p("Most points lie close to the diagonal, indicating strong alignment. Two large projects (over €400M) deviate slightly, suggesting minor inconsistencies."),

        output_widget("plot_ec_diff_quantiles"),
        ui.p("14,258 projects report an exact match (ec_diff = 0). Others are spread across quantile-based bins from underfunding to excess funding up to €20M."),

        output_widget("plot_cost_diff_quantiles"),
        ui.p("14,271 projects show exact cost agreement. Remaining projects range from €-200M underreporting to €20M overreporting at the org level.")
    )

    )
)