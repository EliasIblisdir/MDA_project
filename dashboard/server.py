from shiny import render
from shinywidgets import render_plotly, render_widget
import plotly.express as px
import ipywidgets as widgets
import pandas as pd
import os
import pycountry

# Load in data files from Data folder
DATA = os.path.join(os.path.dirname(__file__), "..", "Data")

project_financials = pd.read_pickle(os.path.join(DATA, "finance.pkl"))
projects = pd.read_pickle(os.path.join(DATA, "projects.pkl"))
organizations = pd.read_pickle(os.path.join(DATA, "organizations.pkl"))
deliverables = pd.read_pickle(os.path.join(DATA, "deliverables.pkl"))
publications = pd.read_pickle(os.path.join(DATA, "publications.pkl"))
reports = pd.read_pickle(os.path.join(DATA,"reports.pkl"))
data = pd.read_pickle(os.path.join(DATA,"PE.pkl"))


# Server Logic

def server(input, output, session):

    @output
    @render.data_frame
    def data_preview():
        return project_financials



    @output
    @render_plotly
    def plot_ec_scatter():
        fig = px.scatter(
            project_financials,
            x="ecMaxContribution",
            y="sum_ecContribution",
            hover_data=["id", "acronym"],
            trendline="ols",
            title="Project EU Funding vs Sum of Org EC Contributions"
        )
        return fig

    @output
    @render_plotly
    def plot_ec_diff():
        import plotly.express as px
        fig = px.histogram(
            project_financials,
            x="ec_diff",
            nbins=100,
            title="Difference: ecMaxContribution - Sum of Org ecContribution"
        )
        return fig
    
    @output
    @render_plotly
    def plot_ec_diff_quantiles():
        import pandas as pd
        import plotly.express as px

        df = project_financials.copy()
        df = df[df["ec_diff"].notna()]

        # Define bin edges
        bin_edges = [-120_000_000, -1e-9, 15_000, 60_000, 115_000, 230_000, 510_000, 20_000_000]

        # Create IntervalIndex
        intervals = pd.IntervalIndex.from_breaks(bin_edges, closed="right")

        # Use pd.cut to bin values
        df["ec_diff_bin"] = pd.cut(df["ec_diff"], bins=intervals)

        # Format interval labels into human-friendly form
        def format_interval(interval):
            left = interval.left
            right = interval.right

            def fmt(v):
                if abs(v) >= 1_000_000:
                    return f"{v/1_000_000:.1f}M"
                elif abs(v) >= 1_000:
                    return f"{v/1_000:.0f}K"
                else:
                    return f"{v:.0f}"

            if left < 0 and right < 0:
                return f"< 0"
            return f"{fmt(left)} – {fmt(right)}"

        # Map to readable labels
        label_map = {iv: format_interval(iv) for iv in intervals}
        df["bin_label"] = df["ec_diff_bin"].map(label_map)

        # Ensure the bin_label column is Categorical
        df["bin_label"] = df["bin_label"].astype("category")

        # Add "0 (Exact Match)" as a valid category
        df["bin_label"] = df["bin_label"].cat.add_categories("0 (Exact Match)")

        # Now safely assign
        df.loc[df["ec_diff"] == 0, "bin_label"] = "0 (Exact Match)"


        # Compute counts
        bin_order = ["< 0", "0 (Exact Match)"] + [label for label in label_map.values() if label != "< 0"]
        bin_counts = (
            df["bin_label"]
            .value_counts()
            .reindex(bin_order)  # preserve readable order
            .reset_index(name="count")
            .rename(columns={"index": "bin_label"})
            .dropna()
        )

        # Plot
        fig = px.bar(
            bin_counts,
            x="bin_label",
            y="count",
            title="ec_diff Distribution with Financial-Friendly Bins",
            labels={"bin_label": "ec_diff Range", "count": "Number of Projects"},
        )
        fig.update_layout(xaxis_tickangle=45)

        return fig



        
    @output
    @render_plotly
    def plot_cost_diff_quantiles():
        import pandas as pd
        import plotly.express as px

        df = project_financials.copy()
        df = df[df["cost_diff"].notna()]

        # Define custom bin edges
        bin_edges = [-210_000_000, -270_000, -94_000, -7_000, 0, 2_000, 52_000, 125_000, 250_000, 510_000, 20_000_000]
        intervals = pd.IntervalIndex.from_breaks(bin_edges, closed="right")

        # Bin non-zero values
        df["cost_diff_bin"] = pd.cut(df["cost_diff"], bins=intervals)

        # Convert to readable labels
        def fmt_val(v):
            if abs(v) >= 1_000_000:
                return f"{v/1_000_000:.1f}M"
            elif abs(v) >= 1_000:
                return f"{v/1_000:.0f}K"
            return str(int(v))

        def label_interval(interval):
            if interval.left < 0 and interval.right <= 0:
                return f"{fmt_val(interval.left)} – {fmt_val(interval.right)}"
            elif interval.left < 0 and interval.right > 0:
                return "< 0"
            else:
                return f"{fmt_val(interval.left)} – {fmt_val(interval.right)}"

        label_map = {iv: label_interval(iv) for iv in intervals}
        df["bin_label"] = df["cost_diff_bin"].map(label_map)

        # Add "0 (Exact Match)" category
        df["bin_label"] = df["bin_label"].astype("category")
        df["bin_label"] = df["bin_label"].cat.add_categories("0 (Exact Match)")
        df.loc[df["cost_diff"] == 0, "bin_label"] = "0 (Exact Match)"

        # Prepare counts in correct order
        # Generate labels in order
        labels_in_order = [label_map[iv] for iv in intervals]

        # Insert "0 (Exact Match)" after the bin that ends at 0
        insert_index = next(
            (i + 1 for i, iv in enumerate(intervals) if iv.right == 0),
            len(labels_in_order) // 2  # fallback: middle
        )

        bin_order = labels_in_order[:insert_index] + ["0 (Exact Match)"] + labels_in_order[insert_index:]


        bin_counts = (
            df["bin_label"]
            .value_counts()
            .reindex(bin_order)
            .reset_index(name="count")
            .rename(columns={"index": "bin_label"})
            .dropna()
        )

        # Plot
        fig = px.bar(
            bin_counts,
            x="bin_label",
            y="count",
            title="cost_diff Distribution with Custom Financial Bins",
            labels={"bin_label": "cost_diff Range", "count": "Number of Projects"},
        )
        fig.update_layout(xaxis_tickangle=45)

        return fig
    

    
    @output
    @render_widget
    def europe_map():
            # Use global `data` which is assumed to be preloaded
            global data

            # Convert ISO-2 to ISO-3 if needed
            if "iso3" not in data.columns:
                def iso2_to_iso3(iso2_code):
                    try:
                        return pycountry.countries.get(alpha_2=iso2_code).alpha_3
                    except:
                        return None

                data["iso3"] = data["coordinator_country"].apply(iso2_to_iso3)

            # Drop rows where ISO-3 conversion failed
            filtered_data = data.dropna(subset=["iso3"])

            # Plot
            fig = px.choropleth(
                filtered_data,
                locations="iso3",                # ISO-3 codes
                color="org_sum_ecContribution",           # Numeric value
                hover_name="coordinator_country",            # Hover label
                color_continuous_scale="Blues",
                projection="natural earth",
                scope="europe"
            )

            fig.update_layout(
                title="Total EU Funding by Country",
                margin={"r": 0, "t": 30, "l": 0, "b": 0}
            )

            return fig


