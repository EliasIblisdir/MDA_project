from shiny import App, ui, render, reactive
from shinywidgets import render_plotly
import plotly.express as px
import plotly.graph_objects as go
#from Horizon import get_funding_summary

#funding_summary = get_funding_summary()

# --- Country data ---
countries_data = {
    "Andorra": 1, "United Arab Emirates": 5, "Afghanistan": 1, "Anguilla": 1, "Albania": 47, 
    "Armenia": 21, "Angola": 7, "Argentina": 108, "Austria": 2902, "Australia": 194, "Aruba": 2, 
    "Azerbaijan": 10, "Bosnia and Herzegovina": 54, "Bangladesh": 9, "Belgium": 5576, "Burkina Faso": 24, 
    "Bulgaria": 614, "Burundi": 6, "Benin": 10, "Bolivia": 7, "Bonaire, Sint Eustatius and Saba": 2, 
    "Brazil": 122, "Bhutan": 1, "Botswana": 6, "Canada": 227, "Democratic Republic of the Congo": 35, 
    "Central African Republic": 2, "Republic of the Congo": 5, "Switzerland": 2356, "Ivory Coast": 19, 
    "Chile": 59, "Cameroon": 19, "China": 212, "Colombia": 62, "Costa Rica": 13, "Cuba": 14, 
    "Cape Verde": 15, "Cyprus": 870, "Czech Republic": 1393, "Germany": 11264, "Djibouti": 1, 
    "Denmark": 2495, "Dominican Republic": 1, "Algeria": 8, "Ecuador": 11, "Estonia": 650, 
    "Egypt": 39, "Greece": 4498, "Spain": 11234, "Ethiopia": 50, "Finland": 2444, "Fiji": 1, 
    "Faroe Islands": 17, "France": 9380, "Gabon": 10, "Georgia": 48, "Ghana": 66, "Gibraltar": 1, 
    "Greenland": 12, "Gambia": 3, "Guinea": 7, "Equatorial Guinea": 1, "Guatemala": 2, "Guam": 1, 
    "Guinea-Bissau": 3, "Hong Kong": 10, "Croatia": 543, "Haiti": 1, "Hungary": 793, "Indonesia": 10, 
    "Ireland": 1893, "Israel": 877, "Isle of Man": 1, "India": 62, "Iraq": 2, "Iran": 4, "Iceland": 146, 
    "Italy": 9730, "Jordan": 9, "Japan": 136, "Kenya": 133, "Kyrgyzstan": 9, "Cambodia": 5, "South Korea": 75, 
    "Kuwait": 1, "Kazakhstan": 14, "Laos": 1, "Lebanon": 24, "Liechtenstein": 4, "Sri Lanka": 6, "Liberia": 5, 
    "Lesotho": 1, "Lithuania": 527, "Luxembourg": 460, "Latvia": 350, "Libya": 1, "Morocco": 62, "Monaco": 4, 
    "Moldova": 66, "Montenegro": 32, "Madagascar": 12, "Marshall Islands": 2, "North Macedonia": 71, 
    "Mali": 7, "Mongolia": 4, "Macau": 1, "Mauritania": 2, "Malta": 186, "Mauritius": 6, "Maldives": 1, 
    "Malawi": 8, "Mexico": 37, "Malaysia": 18, "Mozambique": 29, "Namibia": 8, "New Caledonia": 1, 
    "Niger": 1, "Nigeria": 47, "Nicaragua": 1, "Netherlands": 6319, "Norway": 2309, "Nepal": 2, 
    "New Zealand": 42, "Panama": 2, "Peru": 19, "French Polynesia": 3, "Papua New Guinea": 2, "Philippines": 11, 
    "Pakistan": 12, "Poland": 1787, "Palestine": 4, "Portugal": 2781, "Paraguay": 2, "Qatar": 1, 
    "Romania": 1099, "Serbia": 466, "Rwanda": 26, "Saudi Arabia": 8, "Sudan": 1, "Sweden": 2832, "Singapore": 24, 
    "Slovenia": 1097, "Slovakia": 430, "Sierra Leone": 2, "Senegal": 40, "Suriname": 1, "São Tomé and Príncipe": 6, 
    "El Salvador": 1, "Swaziland": 3, "Chad": 1, "Togo": 2, "Thailand": 46, "Tajikistan": 3, 
    "Turkmenistan": 2, "Tunisia": 69, "Turkey": 917, "Taiwan": 22, "Tanzania": 60, "Ukraine": 335, 
    "Uganda": 76, "United Kingdom": 4310, "United States": 1059, "Uruguay": 9, "Uzbekistan": 21, 
    "Vatican City": 1, "Venezuela": 1, "Vietnam": 18, "Kosovo": 16, "South Africa": 200, "Zambia": 22, "Zimbabwe": 5
}


# --- Filter helper ---
def filter_countries(min_obs):
    return [country for country, count in countries_data.items() if count >= min_obs]

# --- UI ---
app_ui = ui.page_fluid(
    ui.h2("CORDIS Horizon Europe Dashboard - Group 22"),

    ui.navset_tab(
        ui.nav_panel(
            "Country View",
            ui.layout_sidebar(
                ui.sidebar(
                    ui.input_slider("min_observations", "Minimum observations", min=1, max=200, value=100),
                    ui.output_ui("country_select")
                ),
                ui.div(
                    ui.output_plot("europe_map"),
                    ui.output_plot("funding_dist"),
                    ui.output_plot("nlp_pie")
                )
            )
        ),
        ui.nav_panel(
            "Cross-Country Comparison",
            ui.layout_sidebar(
                ui.sidebar(
                    ui.input_select("metric", "Compare countries by",
                                    choices=["Total Funding", "Number of Projects", "Average Contribution"])
                ),
                ui.div(
                    ui.output_plot("sankey_chart"),
                    ui.output_plot("comparison_chart")
                )
            )
        )
    )
)

# --- Server logic ---
def server(input, output, session):

    @reactive.Calc
    def filtered_countries():
        min_obs = input.min_observations()
        return [country for country, count in countries_data.items() if count >= min_obs]

    def country_select_ui():
        filtered = filtered_countries()
        return ui.input_select(
            "country",
            "Select a country",
            choices=filtered,
            selected=filtered[0] if filtered else None
        )

    output.country_select = render.ui(country_select_ui)

    def europe_map():
        df = funding_summary.dropna(subset=["iso_alpha"])  # remove countries without ISO codes
        fig = px.choropleth(
            df,
            locations="iso_alpha",
            color="total_funding",
            hover_name="country",
            hover_data={"project_count": True, "avg_funding": True, "iso_alpha": False},
            color_continuous_scale="Blues",
            title="Total Funding by Country"
        )
        fig.update_geos(fitbounds="locations", visible=False)
        fig.update_layout(
            paper_bgcolor="white",
            plot_bgcolor="lightgrey",
            geo=dict(showframe=False, projection_type="natural earth")
        )
        return fig


    def funding_dist():
        if "country" not in input:
            return go.Figure()
        df = px.data.tips()
        fig = px.histogram(df, x="tip", color_discrete_sequence=["grey"])
        fig.update_layout(title_text=f"Funding Distribution - {input.country()}")
        return fig

    def nlp_pie():
        if "country" not in input:
            return go.Figure()
        labels = ["Health", "AI", "Climate", "Transport"]
        values = [30, 25, 25, 20]
        fig = go.Figure(data=[go.Pie(labels=labels, values=values)])
        fig.update_layout(title_text=f"Topic Distribution - {input.country()}")
        return fig

    def sankey_chart():
        fig = go.Figure(data=[go.Sankey(
            node=dict(
                label=["Country A", "Health", "AI"],
                pad=15, thickness=20, line=dict(color="black", width=0.5)
            ),
            link=dict(source=[0, 0], target=[1, 2], value=[8, 4])
        )])
        fig.update_layout(title_text="Sankey: Countries → Topics → Funding")
        return fig

    def comparison_chart():
        df = px.data.gapminder().query("year == 2007 and continent == 'Europe'")
        fig = px.bar(df, x="country", y="gdpPercap", title="Average Funding (placeholder)")
        return fig

    output.europe_map = render_plotly(europe_map)
    output.funding_dist = render_plotly(funding_dist)
    output.nlp_pie = render_plotly(nlp_pie)
    output.sankey_chart = render_plotly(sankey_chart)
    output.comparison_chart = render_plotly(comparison_chart)

# --- Launch app ---
app = App(app_ui, server)