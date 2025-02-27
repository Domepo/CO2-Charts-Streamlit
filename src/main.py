import streamlit as st
import csv
import catppuccin
import matplotlib as mpl
import matplotlib.pyplot as plt
mpl.style.use(catppuccin.PALETTE.mocha.identifier)

# Setze das Seitenlayout auf "wide"
st.set_page_config(page_title="CO₂-Emissionen Charts", layout="wide")

class CO2Charts:
    """
    Klasse zur Verarbeitung der Energie- und CO₂-Daten.
    """
    def __init__(self, energy_path, co2_path):
        self.energy_path = energy_path
        self.co2_path = co2_path

    def lese_energy(self):
        """
        Liest Bevölkerungsdaten aus der CSV-Datei und gibt ein Dictionary zurück,
        in dem pro Land die jährlichen Bevölkerungszahlen gespeichert sind.
        """
        bev_dict = {}
        with open(self.energy_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                country = row["country"]
                try:
                    year = int(row["year"])
                except ValueError:
                    continue  # Ungültiges Jahr überspringen
                population = self._parse_int(row["population"])
                if country not in bev_dict:
                    bev_dict[country] = {}
                bev_dict[country][year] = population
        return bev_dict

    def lese_emissionen(self, countries):
        """
        Liest CO₂-Emissionen pro Kopf für die angegebenen Länder.
        """
        if isinstance(countries, str):
            countries = [countries]
        emissions_dict = {country: {} for country in countries}
        with open(self.co2_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                country = row["Entity"]
                if country in countries:
                    try:
                        year = int(row["Year"])
                    except ValueError:
                        continue  # Ungültiges Jahr überspringen
                    emissions = self._parse_float(row["Annual CO₂ emissions (per capita)"])
                    emissions_dict[country][year] = emissions
        return emissions_dict

    def get_available_countries(self):
        """
        Gibt eine alphabetisch sortierte Liste aller Länder zurück,
        die in der CO₂-Daten-Datei vorhanden sind.
        """
        countries = set()
        with open(self.co2_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                countries.add(row["Entity"])
        return sorted(countries)

    @staticmethod
    def _parse_int(value):
        value = value.strip()
        if value:
            try:
                return int(value)
            except ValueError:
                return None
        return None

    @staticmethod
    def _parse_float(value):
        value = value.strip()
        if value:
            try:
                return float(value)
            except ValueError:
                return None
        return None

def plot_co2_emission_per_capita(co2_data, countries_colors):
    # Größere Figur für breitere Darstellung
    fig, ax = plt.subplots(figsize=(14, 8))
    for country, color in countries_colors:
        if country in co2_data:
            years = sorted(co2_data[country].keys())
            emissions = [co2_data[country][year] for year in years]
            ax.plot(years, emissions, label=country, color=color)
    ax.set_title("CO₂-Emissionen pro Kopf")
    ax.set_xlabel("Jahr")
    ax.set_ylabel("CO₂-Emissionen pro Kopf (t)")
    ax.legend()
    return fig

def plot_absolut_co2_emissions(co2_data, pop_data, countries_colors):
    fig, ax = plt.subplots(figsize=(14, 8))
    for country, color in countries_colors:
        if country in co2_data and country in pop_data:
            years = sorted(set(co2_data[country].keys()) & set(pop_data[country].keys()))
            absolute_emissionen = []
            for year in years:
                emissions = co2_data[country].get(year)
                population = pop_data[country].get(year)
                if emissions is None or population is None:
                    absolute_emissionen.append(None)
                else:
                    absolute_emissionen.append(emissions * population)
            ax.plot(years, absolute_emissionen, label=country, color=color)
    ax.set_title("Absolute CO₂-Emissionen")
    ax.set_xlabel("Jahr")
    ax.set_ylabel("Absolute CO₂-Emissionen (t)")
    ax.legend()
    return fig

def plot_co2_emission_changes(co2_data, countries_colors):
    fig, ax = plt.subplots(figsize=(14, 8))
    for country, color in countries_colors:
        if country in co2_data:
            years = sorted(co2_data[country].keys())
            emissions = [co2_data[country][year] if co2_data[country][year] is not None else 0 for year in years]
            yearly_changes = [emissions[i] - emissions[i - 1] for i in range(1, len(emissions))]
            change_years = years[1:]
            ax.plot(change_years, yearly_changes, label=country, color=color)
        else:
            st.write("Warnung: Keine Daten für", country)
    ax.set_title("Jährliche Änderung der CO₂-Emissionen pro Kopf")
    ax.set_xlabel("Jahr")
    ax.set_ylabel("Änderung der CO₂-Emissionen pro Kopf (t)")
    ax.legend()
    return fig

def plot_co2_emission_change_change(co2_data, countries_colors):
    fig, ax = plt.subplots(figsize=(14, 8))
    for country, color in countries_colors:
        if country in co2_data:
            years = sorted(co2_data[country].keys())
            emissions = [co2_data[country][year] for year in years]
            first_alternation = [emissions[i] - emissions[i - 1] for i in range(1, len(emissions))]
            second_alternation = [first_alternation[i] - first_alternation[i - 1] for i in range(1, len(first_alternation))]
            years_second_alternation = years[2:]
            ax.plot(years_second_alternation, second_alternation, label=country, color=color)
    ax.set_title("Änderung der jährlichen Änderung der CO₂-Emissionen pro Kopf")
    ax.set_xlabel("Jahr")
    ax.set_ylabel("Änderung der Änderung (Emission pro Kopf)")
    ax.legend()
    return fig

def main():
    st.title("CO₂-Emissionen Charts")
    st.write("Wähle die Länder aus, für die du die Diagramme anzeigen möchtest.")

    # Dateipfade zu den CSV-Dateien
    energy_file = r"assets/energy.csv"
    co2_file = r"assets/co2-emissions.csv"

    charts = CO2Charts(energy_file, co2_file)
    
    # Lese alle verfügbaren Länder aus der CO₂-Daten-Datei
    available_countries = charts.get_available_countries()
    
    # Multiselect-Widget für Länder
    selected_countries = st.multiselect("Länder auswählen", available_countries, default=["Poland", "Malaysia"])
    if not selected_countries:
        st.warning("Bitte wähle mindestens ein Land aus.")
        return

    # Weise jedem ausgewählten Land eine Farbe aus dem Standard-Matplotlib-Farbschema zu
    color_palette = plt.rcParams['axes.prop_cycle'].by_key()['color']
    countries_colors = [(country, color_palette[i % len(color_palette)]) for i, country in enumerate(selected_countries)]
    
    with st.spinner("Lade Daten..."):
        co2_data = charts.lese_emissionen(selected_countries)
        pop_data = charts.lese_energy()

    # Die beiden Diagramme nebeneinander anordnen
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("CO₂-Emissionen pro Kopf")
        fig1 = plot_co2_emission_per_capita(co2_data, countries_colors)
        st.pyplot(fig1)
    with col2:
        st.subheader("Absolute CO₂-Emissionen")
        fig2 = plot_absolut_co2_emissions(co2_data, pop_data, countries_colors)
        st.pyplot(fig2)

    col3, col4 = st.columns(2)
    with col3:
        st.subheader("Jährliche Änderung der CO₂-Emissionen pro Kopf")
        fig3 = plot_co2_emission_changes(co2_data, countries_colors)
        st.pyplot(fig3)
    with col4:
        st.subheader("Änderung der jährlichen Änderung der CO₂-Emissionen pro Kopf")
        fig4 = plot_co2_emission_change_change(co2_data, countries_colors)
        st.pyplot(fig4)

if __name__ == '__main__':
    main()
