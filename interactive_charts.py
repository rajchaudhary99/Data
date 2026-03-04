import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.widgets import Button, RadioButtons

df = pd.read_excel("Year_vs_Month_Monthly_Average_Ozone_Pivot_Rounded.xlsx")
df_long = df.melt(id_vars=['Year'], var_name='Month', value_name='Value')
yearly_total = df_long.groupby('Year')['Value'].sum()
monthly_avg = df_long.groupby('Month')['Value'].mean()

fig = plt.figure(figsize=(14, 8))
ax_chart = plt.subplot2grid((1, 5), (0, 0), colspan=4)
ax_radio = plt.subplot2grid((1, 5), (0, 4))

def draw_chart(chart_type):
    ax_chart.clear()
    
    if chart_type == 'Bar - Yearly':
        bars = ax_chart.bar(yearly_total.index, yearly_total.values, color='skyblue')
        ax_chart.set_title("Yearly Total Ozone")
        ax_chart.set_xlabel("Year")
        ax_chart.set_ylabel("Total Value")
        for bar in bars:
            height = bar.get_height()
            ax_chart.text(bar.get_x() + bar.get_width()/2., height, f'{height:.0f}', ha='center', va='bottom')
    
    elif chart_type == 'Line - Yearly':
        ax_chart.plot(yearly_total.index, yearly_total.values, marker='o', color='green', linewidth=2)
        ax_chart.set_title("Yearly Ozone Trend")
        ax_chart.set_xlabel("Year")
        ax_chart.set_ylabel("Total Value")
        ax_chart.grid(True)
        for x, y in zip(yearly_total.index, yearly_total.values):
            ax_chart.annotate(f'{y:.0f}', (x, y), textcoords="offset points", xytext=(0,8), ha='center')
    
    elif chart_type == 'Bar - Monthly':
        bars = ax_chart.barh(monthly_avg.index, monthly_avg.values, color='coral')
        ax_chart.set_title("Monthly Average Ozone")
        ax_chart.set_xlabel("Average Value")
        ax_chart.set_ylabel("Month")
        for bar in bars:
            width = bar.get_width()
            ax_chart.text(width, bar.get_y() + bar.get_height()/2., f'{width:.1f}', ha='left', va='center')
    
    elif chart_type == 'Pie - Monthly':
        ax_chart.pie(monthly_avg.values, labels=monthly_avg.index, autopct='%1.1f%%', startangle=90)
        ax_chart.set_title("Monthly Ozone Distribution")
    
    elif chart_type == 'Heatmap':
        heatmap_data = df.set_index('Year').T
        im = ax_chart.imshow(heatmap_data, aspect='auto', cmap='YlOrRd')
        ax_chart.set_title("Ozone Heatmap: Year vs Month")
        ax_chart.set_xlabel("Year")
        ax_chart.set_ylabel("Month")
        ax_chart.set_xticks(range(len(df['Year'])))
        ax_chart.set_xticklabels(df['Year'], rotation=45)
        ax_chart.set_yticks(range(len(df.columns[1:])))
        ax_chart.set_yticklabels(df.columns[1:])
        plt.colorbar(im, ax=ax_chart)
    
    elif chart_type == 'Area - Yearly':
        ax_chart.fill_between(yearly_total.index, yearly_total.values, color='lightblue', alpha=0.7)
        ax_chart.plot(yearly_total.index, yearly_total.values, color='blue', linewidth=2)
        ax_chart.set_title("Yearly Ozone Area Chart")
        ax_chart.set_xlabel("Year")
        ax_chart.set_ylabel("Total Value")
        ax_chart.grid(True)
    
    plt.draw()

radio = RadioButtons(ax_radio, ('Bar - Yearly', 'Line - Yearly', 'Bar - Monthly', 'Pie - Monthly', 'Heatmap', 'Area - Yearly'))
radio.on_clicked(draw_chart)

draw_chart('Bar - Yearly')
plt.tight_layout()
plt.show()
