import numpy as np
import pandas as pd
import geopandas as gpd
# import matplotlib.pyplot as plt
from shiny import App, render, ui, reactive, run_app
from shinywidgets import output_widget, render_widget
import plotly.express as px
# import json
import plotly.graph_objects as go



euroSciVoc = pd.read_excel('datasets/euroSciVoc.xlsx')
legalBasis = pd.read_excel('datasets/legalBasis.xlsx')
organization = pd.read_excel('datasets/organization.xlsx')
project = pd.read_excel('datasets/project.xlsx')
topics = pd.read_excel('datasets/topics.xlsx')
webItem = pd.read_excel('datasets/webItem.xlsx')
webLink = pd.read_excel('datasets/webLink.xlsx')

print(organization['ecContribution'].sum())

# Joining the tables

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

"""## Focusing on the 10 most funded countries"""

# Determine top 10 countries by total funding
top_countries = df.groupby("country")["ecContribution"].sum().nlargest(10).index.tolist()
df["country"] = df["country"].apply(lambda x: x if x in top_countries else "Others")


industry = df["euroSciVocPath"].str.split("/").str[1]
df["Industry"] = industry

top_countries = df.groupby("country")["ecContribution"].sum().nlargest(10).index.tolist()
df["country"] = df["country"].apply(lambda x: x if x in top_countries else "Others")

df_grouped = df.groupby(["fundingScheme", "country", "Industry", "SME"]).agg({"ecContribution": "sum"}).reset_index()

labels = ["Total Funding"]
funding_schemes = df_grouped["fundingScheme"].unique().tolist()
countries = df_grouped["country"].unique().tolist()
industries = df_grouped["Industry"].unique().tolist()
smes = df_grouped["SME"].unique().tolist()

labels.extend(funding_schemes)
labels.extend(countries)
labels.extend(industries)
labels.extend(smes)

label_to_index = {label: i for i, label in enumerate(labels)}

colors = []
colors.append("#1f77b4")
colors.extend(["#2ca02c"] * len(funding_schemes))
colors.extend(["#ff7f0e"] * len(countries))
colors.extend(["#9467bd"] * len(industries))
colors.extend(["#d62728"] * len(smes))

sources, targets, values, hover_texts = [], [], [], []


def build_sankey(df):
    for scheme in funding_schemes:
        total = df_grouped[df_grouped["fundingScheme"] == scheme]["ecContribution"].sum()
        sources.append(label_to_index["Total Funding"])
        targets.append(label_to_index[scheme])
        values.append(total)
        hover_texts.append(f"Funding to Scheme {scheme}: €{total:,.0f}")

    for _, row in df_grouped.iterrows():
        sources.append(label_to_index[row["fundingScheme"]])
        targets.append(label_to_index[row["country"]])
        values.append(row["ecContribution"])
        hover_texts.append(f"Scheme {row['fundingScheme']} to {row['country']}: €{row['ecContribution']:,.0f}")

        sources.append(label_to_index[row["country"]])
        targets.append(label_to_index[row["Industry"]])
        values.append(row["ecContribution"])
        hover_texts.append(f"{row['country']} to Industry {row['Industry']}: €{row['ecContribution']:,.0f}")

        sources.append(label_to_index[row["Industry"]])
        targets.append(label_to_index[row["SME"]])
        values.append(row["ecContribution"])
        hover_texts.append(f"Industry {row['Industry']} to SME {row['SME']}: €{row['ecContribution']:,.0f}")

    fig = go.Figure(go.Sankey(
        arrangement="snap",
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=labels,
            color=colors
        ),
        link=dict(
            source=sources,
            target=targets,
            value=values,
            hovertemplate=hover_texts
        )
    ))
    fig.update_layout(
        annotations=[
            dict(
                x=0,
                y=0.85,
                xref='paper',
                yref='paper',
                text='Total Funding',
                showarrow=False,
                font=dict(size=14, color='blue'),
                align='left'
            ),
            dict(
                x=0.22,
                y=1.1,
                xref='paper',
                yref='paper',
                text='Funding Scheme',
                showarrow=False,
                font=dict(size=14, color='blue')
            ),
            dict(
                x=0.5,
                y=0.85,
                xref='paper',
                yref='paper',
                text='Countries',
                showarrow=False,
                font=dict(size=14, color='blue')
            ),
            dict(
                x=0.8,
                y=0.75,
                xref='paper',
                yref='paper',
                text='Sectors/Industries',
                showarrow=False,
                font=dict(size=14, color='blue')
            ),
            dict(
                x=1,
                y=0.7,
                xref='paper',
                yref='paper',
                text='SME',
                showarrow=False,
                font=dict(size=14, color='blue')
            ),
        ]
        )

    return fig






# Formula for the GINI Coefficient (to be calculated per country, across Industry or fundingScheme)

country_funding = df.groupby("country")["ecContribution"].sum()

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

gini_value = gini(country_funding.values)

print(f"Gini coefficient across countries: {gini_value:.3f}")

# def server(input, output, session):
#     @output_widget
#     @render_widget
#     def sankey_plot():
#         return build_sankey(df_raw)

# app = App(app_ui, server)

# # Run the app (opens in browser)
# run_app(app, asyncio_mode='auto')

# # Group and aggregate the data
# df_grouped = df.groupby(["fundingScheme", "country", "Industry", "SME"]).agg({"ecContribution": "sum"}).reset_index()

# # Prepare Sankey data
# labels = ["Total Funding"]

# funding_schemes = df_grouped["fundingScheme"].unique().tolist()
# countries = df_grouped["country"].unique().tolist()
# industries = df_grouped["Industry"].unique().tolist()
# smes = df_grouped["SME"].unique().tolist()

# labels.extend(funding_schemes)
# labels.extend(countries)
# labels.extend(industries)
# labels.extend(smes)

# label_to_index = {label: i for i, label in enumerate(labels)}

# # Assign colors per stage
# colors = []
# num_funding = len(funding_schemes)
# num_countries = len(countries)
# num_industries = len(industries)
# num_smes = len(smes)

# colors.append("#1f77b4")  # Total Funding
# colors.extend(["#2ca02c"] * num_funding)     # Funding Scheme: green
# colors.extend(["#ff7f0e"] * num_countries)   # Country: orange
# colors.extend(["#9467bd"] * num_industries)  # Industry: purple
# colors.extend(["#d62728"] * num_smes)        # SME: red

# # Build Sankey links
# sources, targets, values, hover_texts = [], [], [], []

# # Total Funding -> Funding Schemes
# for scheme in funding_schemes:
#     total = df_grouped[df_grouped["fundingScheme"] == scheme]["ecContribution"].sum()
#     sources.append(label_to_index["Total Funding"])
#     targets.append(label_to_index[scheme])
#     values.append(total)
#     hover_texts.append(f"Funding to Scheme {scheme}: €{total:,.0f}")

# # Funding Schemes -> Countries
# for _, row in df_grouped.iterrows():
#     sources.append(label_to_index[row["fundingScheme"]])
#     targets.append(label_to_index[row["country"]])
#     values.append(row["ecContribution"])
#     hover_texts.append(f"Scheme {row['fundingScheme']} to {row['country']}: €{row['ecContribution']:,.0f}")

# # Countries -> Industries
#     sources.append(label_to_index[row["country"]])
#     targets.append(label_to_index[row["Industry"]])
#     values.append(row["ecContribution"])
#     hover_texts.append(f"{row['country']} to Industry {row['Industry']}: €{row['ecContribution']:,.0f}")

# # Industries -> SME
#     sources.append(label_to_index[row["Industry"]])
#     targets.append(label_to_index[row["SME"]])
#     values.append(row["ecContribution"])
#     hover_texts.append(f"Industry {row['Industry']} to SME {row['SME']}: €{row['ecContribution']:,.0f}")

# # Sankey Diagram
# fig = go.Figure(go.Sankey(
#     arrangement = "snap",
#     node=dict(
#         pad=15,
#         thickness=20,
#         line=dict(color="black", width=0.5),
#         label=labels,
#         color=colors
#     ),
#     link=dict(
#         source=sources,
#         target=targets,
#         value=values,
#         hovertemplate=hover_texts
#     )
# ))
# fig.update_layout(title_text="Horizon EU Funding Flow (Top 10 Countries)", font_size=14)
# fig.update_layout(
#     annotations=[
#         dict(
#             x=0,
#             y=0.85,
#             xref='paper',
#             yref='paper',
#             text='Total Funding',
#             showarrow=False,
#             font=dict(size=14, color='blue'),
#             align='left'
#         ),
#         dict(
#             x=0.22,
#             y=1.1,
#             xref='paper',
#             yref='paper',
#             text='Funding Scheme',
#             showarrow=False,
#             font=dict(size=14, color='blue')
#         ),
#         dict(
#             x=0.5,
#             y=0.85,
#             xref='paper',
#             yref='paper',
#             text='Countries',
#             showarrow=False,
#             font=dict(size=14, color='blue')
#         ),
#         dict(
#             x=0.8,
#             y=0.75,
#             xref='paper',
#             yref='paper',
#             text='Sectors/Industries',
#             showarrow=False,
#             font=dict(size=14, color='blue')
#         ),
#         dict(
#             x=1,
#             y=0.7,
#             xref='paper',
#             yref='paper',
#             text='SME',
#             showarrow=False,
#             font=dict(size=14, color='blue')
#         ),
#     ]
# )



# Shiny App
app_ui = ui.page_fluid(
    ui.h2("Horizon EU Sankey Diagram of Funding Flows (Top 10 Countries)"),
    ui.div(output_widget("sankey_plot"), style = "margin-top: 2em;")
)

def server(input, output, session):
    @output
    @render_widget
    def sankey_plot():
        return build_sankey(df)

app = App(app_ui, server)
