import pandas as pd
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
import statsmodels.api as sm

# Data inladen
fiets_rentals = pd.read_csv('fietsdata2021_rentals_by_day.csv')
weer_data = pd.read_csv('weather_london.csv')

# Zorg ervoor dat de datums in datetime-formaat staan
fiets_rentals["Day"] = pd.to_datetime(fiets_rentals["Day"])
weer_data["Date"] = pd.to_datetime(weer_data["Unnamed: 0"])  # Zet de juiste kolomnaam om

# Merge de datasets op datum
combined_df = pd.merge(fiets_rentals, weer_data, left_on="Day", right_on="Date", how="inner")

# Verwijder de dubbele datumkolom (we houden "Day")
combined_df.drop(columns=["Date"], inplace=True)

# Streamlit-app titel
st.title("Regressieanalyse: Fietsverhuur en Weer")

# Vertaling van de weerfactoren (wspd is verwijderd)
weerfactoren_mapping = {
    "Gemiddelde Temperatuur (°C)": "tavg",
    "Minimale Temperatuur (°C)": "tmin",
    "Maximale Temperatuur (°C)": "tmax",
    "Neerslag (mm)": "prcp"
}

# Selecteer een weerfactor voor de regressie
weerfactor_nl = st.selectbox("Kies een weerfactor:", list(weerfactoren_mapping.keys()))

# Vind de originele kolomnaam in de dataset
originele_kolomnaam = weerfactoren_mapping[weerfactor_nl]  # Mapping terug naar Engels

# Controleer of de kolom bestaat in de dataset
if originele_kolomnaam not in combined_df.columns:
    st.error(f"Fout: De kolom '{originele_kolomnaam}' bestaat niet in de dataset!")
else:
    # X en Y variabelen
    x = combined_df[originele_kolomnaam]  # Weerfactor (Engelse naam uit de dataset)
    y = combined_df["Total Rentals"]  # Aantal fietsverhuringen

    # Regressiemodel maken
    x_with_constant = sm.add_constant(x)  # Constante toevoegen voor de regressie
    model = sm.OLS(y, x_with_constant).fit()
    r_squared = model.rsquared  # R²-waarde van de regressie
    equation = f"y = {model.params[1]:.2f}x + {model.params[0]:.2f}"  # Regressievergelijking

    # Plot maken met seaborn
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.regplot(x=x, y=y, line_kws={'color': 'red'}, scatter_kws={'alpha': 0.5}, ax=ax)
    ax.set_xlabel(weerfactor_nl)  # Gebruik de Nederlandse naam
    ax.set_ylabel("Aantal Fietsverhuringen")
    ax.set_title(f"Regressie: {weerfactor_nl} vs. Fietsverhuur\nR² = {r_squared:.2f}")
    ax.text(0.05, 0.9, equation, transform=ax.transAxes, fontsize=12, color="red")

    # Toon de plot in Streamlit
    st.pyplot(fig)
