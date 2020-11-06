import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def timeseries_frequency_plot(title, df, df2, timeseries_col, y_col, dStart, dEnd, sample_by='D', xtick_freq ='W', axvline=[np.nan]):
    
    '''This function will aggregate a dataframe by count given two columns, the datetime column and any column used to 
    determine frequency'''
    
    timeseries_vs_y = df[[timeseries_col, y_col]]
    plot_df = timeseries_vs_y.set_index(timeseries_col).resample(sample_by)[y_col].sum()
    df = plot_df[(dStart <= plot_df.index) & (plot_df.index <= dEnd)]
    
    timeseries2_vs_y = df2[[timeseries_col, y_col]]
    plot_df2 = timeseries2_vs_y.set_index(timeseries_col).resample(sample_by)[y_col].sum()
    df2 = plot_df2[(dStart <= plot_df2.index) & (plot_df2.index <= dEnd)]

    ax = plt.figure(figsize=(10, 4)).add_subplot(111)
    xticks = pd.date_range(start=dStart, end=dEnd, freq=xtick_freq)
    
    df.plot(ax = ax, xticks=xticks, color='seagreen')
    df2.plot(ax = ax, xticks=xticks, color='red')

    ax.set_ylabel('$', size = 15)
    ax.set_title(title, fontsize=16)
    ax.set_xticklabels([x.strftime('%h%d\n%Y') for x in xticks])
    
    for axv in axvline:
        ax.axvline(axv, color='r', linestyle='--', lw=2)
    
    ax.ticklabel_format(axis='y', style='plain')
    ax.legend(['Revenue', 'Potential loss from cancellations'])
    ax.tick_params(axis='x', which='major', pad=15)
    plt.setp(ax.xaxis.get_majorticklabels(), ha='right')
    
    plt.show()
    

def cancellations_bar(title, df):

	# Percent of canceled bookings by market segment
	canceled_pct = round(100*df['is_canceled'].value_counts(normalize = True, sort = False)\
                                                        .sort_index(), 2)
                                                        
	# set axis labels for market_segment options
	labels = list(canceled_pct.index)
	x = np.arange(len(labels))
	width = 0.5
	plt.style.use('fivethirtyeight')
	y = [canceled_pct[0], canceled_pct[1]]

	# Create bar chart
	fig, ax = plt.subplots(figsize=(12, 4)) 
	ax.barh(1, canceled_pct[1:2], width, color='red', label = 'canceled')
	ax.barh(0, canceled_pct[:1], width, color='seagreen', label = 'not canceled')

	# Add some text for labels, title and custom x-axis tick labels, etc.
	ax.set_xlabel('Percent of canceled/not canceled bookings')
	ax.set_title(title)
	ax.set_yticks(x)
	ax.set_yticklabels(x)
	ax.legend(fontsize=12)

	for i, v in enumerate(y):
		ax.text(v+0.5, i, str(v) + '%', color='blue', fontweight='bold', fontsize=12)

	fig.tight_layout()

	plt.show()

def daily_loss(df):

    daily_losses = df[df['is_canceled'] == 1][['projected_arrival', 'cost_of_stay']]
    AVG_DAILY_LOSS = daily_losses.set_index('projected_arrival').resample('D')['cost_of_stay'].sum().mean()
    
    return AVG_DAILY_LOSS