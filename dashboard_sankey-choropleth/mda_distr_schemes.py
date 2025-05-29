import json
import pandas as pd
import numpy as np
import geopandas as gpd
from shiny import App, ui, render, reactive
# from shiny.express import render_plotly
from shinywidgets import render_widget, output_widget
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import numpy as np
from sklearn.preprocessing import LabelEncoder



euroSciVoc = pd.read_excel('datasets/euroSciVoc.xlsx')
legalBasis = pd.read_excel('datasets/legalBasis.xlsx')
organization = pd.read_excel('datasets/organization.xlsx')
project = pd.read_excel('datasets/project.xlsx')
topics = pd.read_excel('datasets/topics.xlsx')
webItem = pd.read_excel('datasets/webItem.xlsx')
webLink = pd.read_excel('datasets/webLink.xlsx')

"""### Yielding Variables of interest from the datasets
- Total_Funding: from organization.netEcContribution
- Industry: from euroSciVoc.euroSciVocPath (shallowest path level)
- Funding_Scheme: from project.fundingScheme

"""

print(organization.columns)
print(euroSciVoc.columns)
print(project.columns)

# Joining the tables

# project (-> FundingScheme) has column "id"
# euroSciVoc (-> euroSciVocPath) has column "projectID"
# organization (-> netEcContribution) has columns "country" (i.e. a country code), and "projectID"

project.rename(columns={"id": "projectID"}, inplace=True) # Renames the id column in the project dataset as projectID, to allow merging

df = pd.merge(euroSciVoc, organization, on='projectID', how="inner")
df = pd.merge(df, project, on=['projectID', 'totalCost'], how="inner")

print(df.columns)
print(df.shape)

df.drop_duplicates(inplace=True) # there were no duplicates.
print(df.shape)

print(type(df['ecContribution']))
# Convert columns A and B to numeric, forcing errors to NaN
df[['ecContribution', 'netEcContribution', 'ecMaxContribution', 'totalCost']] = df[['ecContribution', 'netEcContribution', 'ecMaxContribution', 'totalCost']].apply(pd.to_numeric, errors='coerce')
print(type(df['ecContribution']))

print("df['ecMaxContribution'] sum:", df['ecMaxContribution'].sum(), "\n")
print("df['ecContribution'] sum:", df['ecContribution'].sum(), "\n")
print("df['netEcContribution'] sum:", df['netEcContribution'].sum(), "\n")
print("df['totalCost'] sum:", df['totalCost'].sum(), "\n")


Funding = df['ecContribution']
Industry = df['euroSciVocPath']
# Only retaining the first level of euroSciVocPath for Industry:
Industry = Industry.str.split('/').str[1]
Funding_Scheme = df['fundingScheme']
Country = df['country']
SME = df['SME']


# We add a column, Industry, to df:
df['Industry'] = df['euroSciVocPath'].str.split('/').str[1]


Total_Horizon_Funding = Funding.sum()
print(Total_Horizon_Funding)

# A quick Google search reveals that the EU Horizon's total funding amounted to about 93.5 billion euro
# Moreover, 70% of the budget has been earmarked to SMEs.
# https://research-and-innovation.ec.europa.eu/funding/funding-opportunities/funding-programmes-and-open-calls/horizon-europe_en

# Sum of ecContribution: 53569569221

print(df['totalCost'].head())

# Load GeoJSON for Europe
with open("datasets/NUTS_RG_01M_2021_4326_LEVL_0.geojson", "r") as f:
    nuts0_geojson = json.load(f)


# Aggregate funding by country
country_funding = df.groupby("country", as_index=False)["ecContribution"].sum().sort_values(by="ecContribution", ascending=False)
# plt.hist(country_funding["ecContribution"], bins=30)
# plt.xlabel("Funding")
# plt.ylabel("Frequency")
# plt.show()
# print(SME.head())
# print(SME.sum() / SME.shape[0])
# print(SME.sum())
# print(SME.shape)

# Formula for the GINI Coefficient (to be calculated per country, across Industry or fundingScheme)

def gini(array):
    """Compute Gini coefficient from a list or NumPy array of values."""
    array = np.array(array, dtype=np.float64)
    if np.amin(array) < 0:
        array -= np.amin(array)  # Normalize if negative values exist
    if np.amin(array) == 0:
        array += 1e-10  # Prevent division by zero
    array = np.sort(array)
    n = array.shape[0]
    index = np.arange(1, n + 1)
    return ((np.sum((2 * index - n - 1) * array)) / (n * np.sum(array)))


# Coordinates to center map on EU:
minx = -25   # Westernmost (e.g., Azores or west of Portugal if excluded)
maxx = 45    # Easternmost (e.g., Romania, Bulgaria)
miny = 33    # Southernmost (e.g., southern Greece, Malta)
maxy = 72    # Northernmost (e.g., Finland, parts of Scandinavia)


# === Gini Coefficients per Country ===
gini_by_country = df.groupby("country").apply(
    lambda group: np.round(gini(group.groupby("fundingScheme")["ecContribution"].sum().values),2)
).reset_index()
gini_by_country.columns = ["country", "gini"]

gini_by_country.head()

# --- Pre-compute pies for all countries
sme_by_country = df.groupby(["country", "SME"]).size().reset_index(name="count")
funding_by_country = df.groupby(["country", "fundingScheme"]).size().reset_index(name="count")









country_code_to_name = {
    "AT": "Austria",
    "BE": "Belgium",
    "BG": "Bulgaria",
    "CH": "Switzerland",
    "CY": "Cyprus",
    "CZ": "Czech Republic",
    "DE": "Germany",
    "DK": "Denmark",
    "EE": "Estonia",
    "EL": "Greece",
    "ES": "Spain",
    "FI": "Finland",
    "FR": "France",
    "HR": "Croatia",
    "HU": "Hungary",
    "IE": "Ireland",
    "IS": "Iceland",
    "IT": "Italy",
    "LI": "Liechtenstein",
    "LT": "Lithuania",
    "LU": "Luxembourg",
    "LV": "Latvia",
    "MT": "Malta",
    "NL": "Netherlands",
    "NO": "Norway",
    "PL": "Poland",
    "PT": "Portugal",
    "RO": "Romania",
    "SE": "Sweden",
    "SI": "Slovenia",
    "SK": "Slovakia",
    "TR": "Turkey",
    "UK": "United Kingdom"
}






# app_ui = ui.layout_columns(
#     ui.column(3,  # shrink sidebar
#         ui.output_ui("selected_country_ui"),
#     ),
#     ui.column(9,  # expand map and visuals
#         ui.output_plot("map", height="1000px"),  # doubled height
#         ui.div(
#             ui.output_plot("sme_pie", height="250px"),
#             ui.output_plot("funding_pie", height="250px"),
#             style="display: flex; flex-direction: row; gap: 20px; margin-top: 20px;"
#         )
#     )
# )

def choropleth_map_schemes():
    geo_df = pd.DataFrame(nuts0_geojson["features"])
    geo_df["country"] = geo_df["properties"].apply(lambda x: x["CNTR_CODE"])
    geo_df = geo_df.merge(gini_by_country, on="country", how="left")

    fig = px.choropleth(
        geo_df,
        geojson=nuts0_geojson,
        locations="country",
        featureidkey="properties.CNTR_CODE",
        color="gini",
        color_continuous_scale="Turbo",
        range_color=(0, 1),
        title="Gini Coefficient of Funding across EU Horizon Funding Schemes, by Country (Lower Gini coefficients are indicative of a more equal distribution of funding)"
    )
    fig.update_geos(lonaxis_range=[minx, maxx], lataxis_range=[miny, maxy], visible=False)
    fig.update_layout(margin={"r":0,"t":30,"l":0,"b":0})
    return fig


def schemes_pie(country):
    country_name = country_code_to_name.get(country, country)  # fallback to code if name not found
    data = funding_by_country[funding_by_country["country"] == country]
    if data.empty:
        return go.Figure().update_layout(title="No funding scheme data available")
    fig = px.pie(data, names="fundingScheme", values="count", title=f"Funding apportioned by Funding Scheme in: {country_name}")
    return fig

def sme_pie(country):
    country_name = country_code_to_name.get(country, country)  # fallback to code if name not found
    data = sme_by_country[sme_by_country["country"] == country]
    if data.empty:
        return go.Figure().update_layout(title="No SME data available")
    fig = px.pie(data, names="SME", values="count", title=f"Proportion of SMEs funded in {country_name}")
    return fig

# -- UI
app_ui = ui.page_fluid(
    ui.h2("EU Horizon Dashboard: Distribution of Funding across Funding Schemes"),
    ui.input_select("country_select", "Select a Country Code (see map)", choices=sorted(df["country"].dropna().unique())),
    output_widget("map_schemes"),
    ui.div(
        output_widget("sme"),
        output_widget("schemes"),
        style="display: flex; gap: 10px;"
    )
)



# -- Server
def server(input, output, session):

    @output
    @render_widget
    def map_schemes():
        return choropleth_map_schemes()

    @output
    @render_widget
    def sme():
        return sme_pie(input["country_select"]())

    @output
    @render_widget
    def schemes():
        return schemes_pie(input["country_select"]())

# -- Run
app = App(app_ui, server)