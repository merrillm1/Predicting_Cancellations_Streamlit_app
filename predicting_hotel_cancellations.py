import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from prediction_app_functions import timeseries_frequency_plot

st.title('Predicting Hotel Cancellations')

DATE_COLUMN = 'projected_arrival'
DATA_URL = ('https://raw.githubusercontent.com/merrillm1/Predicting_Hotel_Cancellations/'
			'master/Jupyter_Notebooks/data/master_df.csv')
@st.cache
def load_data(nrows):
    data = pd.read_csv(DATA_URL, index_col=0, nrows=nrows)
    data[DATE_COLUMN] = pd.to_datetime(data[DATE_COLUMN])
    return data
    
# Create a text element and let the reader know the data is loading.
data_load_state = st.text('Loading data...')
# Load 10,000 rows of data into the dataframe.
hotels = load_data(50000)
# Notify the reader that the data was successfully loaded.
data_load_state.text("Done! (using st.cache)")

if st.checkbox('Show raw data'):
    st.subheader('Raw data')
    st.write(hotels)


st.set_option('deprecation.showPyplotGlobalUse', False)
dStart = hotels.projected_arrival.min() # start of data
dEnd = hotels.projected_arrival.max() # end of data
raw_plot = timeseries_frequency_plot(
                         'Revenue vs Potential Loss', 
                          hotels[hotels['is_canceled'] == 0],
                          hotels[hotels['is_canceled'] == 1],
                         'projected_arrival', 
                         'cost_of_stay', 
                         dStart,
                         dEnd, 
                         'W', 
                         '2M')

st.pyplot(raw_plot)

df_ota = hotels[hotels['market_segment'] == 'Online TA']
df_direct = hotels[hotels['market_segment'] == 'Direct']
df_other = hotels[(hotels['market_segment'] == 'Corporate') | \
				  (hotels['market_segment'] == 'Complementary') | \
				  (hotels['market_segment'] == 'Aviation')]
				  
df_group = hotels[hotels['market_segment'] == 'Groups']

st.subheader('Data filtering')

st.write('Our prediction algorithm found that group bookings were the most risky with'
		 ' online travel agency bookings coming in second. Direct bookings were reliable'
		 ' source of bookings with only 15% of those bookings resulting in a cancellation'
		 ', compared to 61% of group bookings eventually being canceled!')
st.write('The default percent breakdown is representative of the original dataset, '
		 'which cantained about 37% canceled bookings. Change the settings to see the '
		 'effect on revenue, potential loss and cancelation rate. Choose your combination'
		 ' wisely to lower the loss, good luck!')

max_rows = 100
ota_pct = st.slider('Percent of online travel agency bookings', 0, 100, 50)
direct_pct = st.slider('Percent of direct dookings', 0, 100, 10)
group_pct = st.slider('Percent of group bookings', 0, 100, 15)
other_pct = st.slider('Percent from other sources (corporate, complementary, offline OTA)'
					  , 0, 100, 25)

ota = df_ota.sample(int(ota_pct*max_rows), replace=True, random_state=3, axis=0)
direct = df_direct.sample(int(direct_pct*max_rows), replace=True, random_state=3, axis=0)
other = df_other.sample(int(other_pct*max_rows), replace=True, random_state=3, axis=0)
group = df_group.sample(int(group_pct*max_rows), replace=True, random_state=3, axis=0)

master_df = pd.concat([ota, direct, other, group], ignore_index=True)

st.write('Lead time was the top predictor of cancellations, 2 out of every 3 bookings '
		 'were canceled when booked more than 1 year out compared to 1 out of every 10 '
		 'for reservations made 1 week out or less!')

MAX_LEAD_TIME = st.slider('Lead time Max', 1, 750, 750)
MIN_LEAD_TIME = st.slider('Lead time Min', 0, 700, 0) 

final = master_df[(master_df['lead_time'] <= MAX_LEAD_TIME) |\
				  (master_df['lead_time'] >= MIN_LEAD_TIME)]\
				  .sample(50000, replace=True, random_state=3, axis=0)
  
filtered_plot = timeseries_frequency_plot(
                         'Revenue vs Potential Loss', 
                          final[final['is_canceled'] == 0],
                          final[final['is_canceled'] == 1],
                         'projected_arrival', 
                         'cost_of_stay', 
                         dStart,
                         dEnd, 
                         'W', 
                         '2M')

if st.checkbox('Show results?'):
    st.subheader('The Cost of Cancellations')
    st.pyplot(filtered_plot)

