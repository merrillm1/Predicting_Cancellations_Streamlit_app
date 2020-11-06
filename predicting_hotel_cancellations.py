import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import prediction_app_functions as func

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
hotels = load_data(100000)
# Notify the reader that the data was successfully loaded.
data_load_state.text("Done! (using st.cache)")

st.write('Hello! Thank you for checking out my streamlit app. The purpose of this tool is to explore the'
' data from a project of mine, "Predicting Hotel Cancellations" which you can check out in the link'
' below.')

st.write('Your job is to lower the cancellation rate and potential revenue'
' loss by adjusting parameters such as where customers are booking from, and how much lead time'
' they had before their projected arrival. You can determine how successful your adjustments are '
' by seeing the affect on percentage of cancellations and total potential loss.')

link = '[Project Link](https://github.com/merrillm1/Predicting_Hotel_Cancellations)'
st.markdown(link, unsafe_allow_html=True)

if st.checkbox('Show raw data'):
    st.subheader('Raw data')
    st.write(hotels)

bar_plot = func.cancellations_bar('Raw Data Cancellations', hotels)

st.pyplot(bar_plot)

st.set_option('deprecation.showPyplotGlobalUse', False)
dStart = hotels.projected_arrival.min() # start of data
dEnd = hotels.projected_arrival.max() # end of data
raw_plot = func.timeseries_frequency_plot(
                         'Projected Revenue vs Potential Loss', 
                          hotels,
                          hotels[hotels['is_canceled'] == 1],
                         'projected_arrival', 
                         'cost_of_stay', 
                         dStart,
                         dEnd, 
                         'W', 
                         '2M')

st.pyplot(raw_plot)

raw_loss = func.daily_loss(hotels)

st.write(print("Average daily projected loss".format(round(raw_loss, 2))))

df_ota = hotels[hotels['market_segment'] == 'Online TA']
df_direct = hotels[hotels['market_segment'] == 'Direct']
df_other = hotels[(hotels['market_segment'] == 'Corporate') | \
				  (hotels['market_segment'] == 'Complementary') | \
				  (hotels['market_segment'] == 'Aviation')]
				  
df_group = hotels[hotels['market_segment'] == 'Groups']

st.subheader('Data filtering')

st.write('Try re-distributing the customer market and lead-time range in the left panel'
		' to lower the impact of cancellations. Once you make your selections, check '
		' the boxes below to see the change.')
		 
st.write('Our prediction algorithm found that group bookings were the most risky with'
		 ' online travel agency bookings coming in second. Direct bookings were reliable'
		 ' source of bookings with only 15% of those bookings resulting in a cancellation'
		 ', compared to 61% of group bookings eventually being canceled!')
st.sidebar.write('The default percent breakdown is representative of the original dataset, '
		 'which cantained about 37% canceled bookings. Change the settings to see the '
		 'effect on revenue, potential loss and cancelation rate. Choose your combination'
		 ' wisely to lower the loss, good luck!')

max_rows = 1000
ota_pct = st.sidebar.slider('Percent of online travel agency bookings', 0, 100, 50)
direct_pct = st.sidebar.slider('Percent of direct dookings', 0, 100, 10)
group_pct = st.sidebar.slider('Percent of group bookings', 0, 100, 15)
other_pct = st.sidebar.slider('Percent from other sources (corporate, complementary, offline OTA)'
					  , 0, 100, 25)

ota = df_ota.sample(int(ota_pct*max_rows), replace=True, random_state=3, axis=0)
direct = df_direct.sample(int(direct_pct*max_rows), replace=True, random_state=3, axis=0)
other = df_other.sample(int(other_pct*max_rows), replace=True, random_state=3, axis=0)
group = df_group.sample(int(group_pct*max_rows), replace=True, random_state=3, axis=0)

master_df = pd.concat([ota, direct, other, group], ignore_index=True)

st.sidebar.write('Lead time was the top predictor of cancellations, 2 out of every 3 bookings '
		 'were canceled when booked more than 1 year out compared to 1 out of every 10 '
		 'for reservations made less than 1 week out!')

MAX_LEAD_TIME = st.sidebar.slider('Lead time Max', 1, 750, 750)
MIN_LEAD_TIME = st.sidebar.slider('Lead time Min', 0, 700, 0) 

result = master_df[(master_df['lead_time'] <= int(MAX_LEAD_TIME)) & \
				  (master_df['lead_time'] >= int(MIN_LEAD_TIME))]\

final = result.sample(50000, replace=True, random_state=3, axis=0).reset_index(drop=True)
				  
bar_plot_final = func.cancellations_bar('Impact on Cancellations', final)

if st.checkbox('Show the impact on cancellations?'):
    st.subheader('Based on your adjustments, here are the results:')
    st.pyplot(bar_plot_final)

filtered_plot = func.timeseries_frequency_plot(
                         'Projected Revenue vs Potential Loss', 
                          final,
                          final[final['is_canceled'] == 1],
                         'projected_arrival', 
                         'cost_of_stay', 
                         dStart,
                         dEnd, 
                         'W', 
                         '2M')

adjusted_loss = func.daily_loss(final)

st.write(print("Average daily projected loss".format(round(adjusted_loss, 2))))

if st.checkbox('Show the impact on revenue?'):
	st.subheader('Based on your adjustments, here are the results:')
	st.pyplot(filtered_plot)   

