import streamlit as st
import pandas as pd
import plotly.express as px

# Load the dataset
@st.cache_data
def load_data():
    file_path = "emission.csv"  # Update this path if needed
    df = pd.read_csv(file_path)

    # Identify year columns
    year_columns = [col for col in df.columns if col.isdigit()]

    # Convert to long format
    df_melted = df.melt(id_vars=["Country", "ISO2", "ISO3", "Indicator"], 
                         value_vars=year_columns, var_name="Year", value_name="CO2_Emissions")
    
    df_melted["Year"] = df_melted["Year"].astype(int)

    # Pivot to separate indicators
    df_pivoted = df_melted.pivot_table(index=["Country", "ISO2", "ISO3", "Year"], 
                                       columns="Indicator", values="CO2_Emissions").reset_index()

    # Rename columns
    df_pivoted.columns.name = None
    df_pivoted.rename(columns={
        "CO2 emissions": "CO2_Emissions",
        "CO2 emissions intensities": "CO2_Intensities",
        "CO2 emissions multipliers": "CO2_Multipliers"
    }, inplace=True)

    return df_pivoted

df = load_data()

# Streamlit UI
st.title("🌍 Interactive CO₂ Emissions Dashboard")
st.sidebar.header("Filter Options")

# Dropdown filters
selected_year = st.sidebar.slider("Select Year", min_value=int(df["Year"].min()), max_value=int(df["Year"].max()), value=int(df["Year"].max()))
selected_country = st.sidebar.selectbox("Select Country", ["All"] + sorted(df["Country"].unique()))

# Filter data
df_filtered = df[df["Year"] == selected_year]
if selected_country != "All":
    df_filtered = df_filtered[df_filtered["Country"] == selected_country]

# Total CO₂ Emissions Over Time
fig1 = px.line(df.groupby("Year")["CO2_Emissions"].sum().reset_index(),
               x="Year", y="CO2_Emissions", title="Global CO₂ Emissions Over Time",
               markers=True)
st.plotly_chart(fig1, use_container_width=True)

# Top 10 CO₂ Emitting Countries
top_countries = df_filtered.groupby("Country")["CO2_Emissions"].sum().nlargest(10)
fig2 = px.bar(top_countries, x=top_countries.index, y=top_countries.values,
              title=f"Top 10 CO₂ Emitting Countries in {selected_year}", labels={"y": "CO₂ Emissions"})
st.plotly_chart(fig2, use_container_width=True)

# Scatter Plot: CO₂ Emissions vs Intensities
fig3 = px.scatter(df_filtered, x="CO2_Intensities", y="CO2_Emissions",
                  size="CO2_Multipliers", color="Country", hover_name="Country",
                  title=f"CO₂ Emissions vs Intensities in {selected_year}",
                  labels={"CO2_Intensities": "CO₂ Intensities (Metric Tons per $1M Output)",
                          "CO2_Emissions": "CO₂ Emissions (Million Metric Tons)"})
st.plotly_chart(fig3, use_container_width=True)

# Heatmap for CO₂ Multipliers by Country
fig4 = px.choropleth(df_filtered, locations="ISO3", color="CO2_Multipliers",
                     hover_name="Country", color_continuous_scale="Blues",
                     title=f"CO₂ Multipliers by Country in {selected_year}")
st.plotly_chart(fig4, use_container_width=True)

# Correlation Matrix
st.write("### Correlation Matrix of CO₂ Metrics")
st.dataframe(df_filtered[["CO2_Emissions", "CO2_Intensities", "CO2_Multipliers"]].corr())

# Footer
st.write("Developed by Rahat Sabyrbekov - Data Science Portfolio")
