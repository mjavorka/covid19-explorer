import streamlit as st

import pandas as pd
import matplotlib.pyplot as plt

# https://www.ecdc.europa.eu/en/publications-data/download-todays-data-geographic-distribution-covid-19-cases-worldwide
DATA_URL = ('https://www.ecdc.europa.eu/sites/default/files/documents/'
            'COVID-19-geographic-disbtribution-worldwide-2020-03-15.xls')


@st.cache
def load_data():
    return pd.read_excel(DATA_URL)


def calc_grow_rate(df, new_cases_idx):
    grow_rates = []
    for idx in range(len(df)):
        today = df[new_cases_idx][idx]
        if idx - 1 < 0:
            yesterday = 0
        else:
            yesterday = df[new_cases_idx][idx - 1]

        grow_rate = (today / yesterday) if yesterday != 0 else int(today)
        grow_rates.append(grow_rate)
    return grow_rates


def calc_total(df, new_cases_idx):
    total_confirmed = []
    for idx in range(len(df)):
        total_confirmed.append(sum(df[new_cases_idx][:idx+1]))
    return total_confirmed


geo_distribution = load_data()
geo_distribution['DateRep'] = pd.to_datetime(geo_distribution['DateRep'])

st.title('COVID-19 Geographic distribution')

default_cols = ["DateRep", "CountryExp", "NewConfCases"]
selected_cols = st.multiselect("Columns", geo_distribution.columns.tolist(), default=default_cols)

st.write(geo_distribution.loc[:, selected_cols])

# overall trend
st.write('New cases worldwide')
grouped_by_date = geo_distribution.groupby("DateRep")[['DateRep', 'NewConfCases']].sum().reset_index()
plt.plot('DateRep', 'NewConfCases', data=grouped_by_date)
plt.title('New cases')
plt.legend(['World'], loc=1)
st.pyplot()

st.write('New cases EU/Non-EU')
grouped_by_date_geo = geo_distribution.groupby(["DateRep", "EU"])[['DateRep', 'NewConfCases']].sum().reset_index()
eu_cases = grouped_by_date_geo.loc[grouped_by_date_geo['EU'] == 'EU'].reset_index()
non_eu_cases = (
    grouped_by_date_geo.loc[grouped_by_date_geo['EU'] != 'EU']
    .groupby("DateRep")[['DateRep', 'NewConfCases']]
    .sum()
    .reset_index()
    )
plt.plot('DateRep', 'NewConfCases', data=eu_cases)
plt.plot('DateRep', 'NewConfCases', data=non_eu_cases)
plt.title('New cases')
plt.legend(['EU', 'Non-EU'], loc=1)
st.pyplot()

eu_cases['grow_rate'] = calc_grow_rate(df=eu_cases, new_cases_idx='NewConfCases')
non_eu_cases['grow_rate'] = calc_grow_rate(df=non_eu_cases, new_cases_idx='NewConfCases')

last_days = st.slider('Number of last days?', 0, len(eu_cases), 10)
plt.plot('DateRep', 'grow_rate', data=eu_cases[-last_days:])
plt.plot('DateRep', 'grow_rate', data=non_eu_cases[-last_days:])
plt.axhline(y=1, color='r', linestyle='-')
plt.title('Grow rate')
plt.legend(['EU', 'Non-EU'], loc=1)
st.pyplot()

# default_countries = ["Slovakia", "Czech Republic"]
default_countries = ["Spain", "France", "Italy"]
selected_countries = st.multiselect("Columns", geo_distribution.CountryExp.unique().tolist(), default=default_countries)

selected_countries_data = dict()
for country in selected_countries:
    selected_countries_data[country] = geo_distribution.loc[geo_distribution['CountryExp'] == country]
    selected_countries_data[country] = selected_countries_data[country].sort_values(by='DateRep').reset_index()
    selected_countries_data[country]['total_confirmed'] = calc_total(
        df=selected_countries_data[country], new_cases_idx='NewConfCases'
    )
    selected_countries_data[country]['grow_rate'] = calc_grow_rate(
        df=selected_countries_data[country], new_cases_idx='NewConfCases'
    )

# show table with all selected countries
st.write(pd.concat(selected_countries_data.values()))

plt.title('New cases')
labels = []
for country in selected_countries:
    plt.plot('DateRep', 'NewConfCases', data=selected_countries_data[country])
    labels.append(country)
plt.legend(labels, loc=1)
st.pyplot()

plt.title('Total cases')
labels = []
for country in selected_countries:
    plt.plot('DateRep', 'total_confirmed', data=selected_countries_data[country])
    labels.append(country)
plt.legend(labels, loc=1)
st.pyplot()

plt.title('Grow rate')
labels = []
for country in selected_countries:
    plt.plot('DateRep', 'grow_rate', data=selected_countries_data[country])
    labels.append(country)
plt.axhline(y=1, color='r', linestyle='-')
plt.legend(labels + ['Inflexion point'], loc=1)
st.pyplot()
