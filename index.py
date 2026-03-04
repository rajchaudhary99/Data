import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.widgets import Cursor

df = pd.read_excel("Year_vs_Month_Monthly_Average_Ozone_Pivot_Rounded.xlsx")

df_long = df.melt(id_vars=['Year'], var_name='Month', value_name='Value')
yearly_total = df_long.groupby('Year')['Value'].sum()
monthly_avg = df_long.groupby('Month')['Value'].mean()

fig, axes = plt.subplots(3, 2, figsize=(15, 12))

# 1. Bar Chart - Yearly Total
bars1 = axes[0, 0].bar(yearly_total.index, yearly_total.values, color='skyblue')
axes[0, 0].set_title("Yearly Total Ozone")
axes[0, 0].set_xlabel("Year")
axes[0, 0].set_ylabel("Total Value")
for bar in bars1:
    height = bar.get_height()
    axes[0, 0].text(bar.get_x() + bar.get_width()/2., height, f'{height:.0f}', ha='center', va='bottom', fontsize=8)

# 2. Line Chart - Yearly Trend
line, = axes[0, 1].plot(yearly_total.index, yearly_total.values, marker='o', color='green')
axes[0, 1].set_title("Yearly Ozone Trend")
axes[0, 1].set_xlabel("Year")
axes[0, 1].set_ylabel("Total Value")
axes[0, 1].grid(True)
for x, y in zip(yearly_total.index, yearly_total.values):
    axes[0, 1].annotate(f'{y:.0f}', (x, y), textcoords="offset points", xytext=(0,5), ha='center', fontsize=7)

# 3. Horizontal Bar Chart - Monthly Average
bars3 = axes[1, 0].barh(monthly_avg.index, monthly_avg.values, color='coral')
axes[1, 0].set_title("Monthly Average Ozone")
axes[1, 0].set_xlabel("Average Value")
axes[1, 0].set_ylabel("Month")
for bar in bars3:
    width = bar.get_width()
    axes[1, 0].text(width, bar.get_y() + bar.get_height()/2., f'{width:.1f}', ha='left', va='center', fontsize=8)

# 4. Pie Chart - Monthly Distribution
wedges, texts, autotexts = axes[1, 1].pie(monthly_avg.values, labels=monthly_avg.index, autopct='%1.1f%%', startangle=90)
axes[1, 1].set_title("Monthly Ozone Distribution")
for autotext in autotexts:
    autotext.set_color('white')
    autotext.set_fontsize(8)

# 5. Heatmap - Year vs Month
heatmap_data = df.set_index('Year').T
im = axes[2, 0].imshow(heatmap_data, aspect='auto', cmap='YlOrRd')
axes[2, 0].set_title("Ozone Heatmap: Year vs Month")
axes[2, 0].set_xlabel("Year")
axes[2, 0].set_ylabel("Month")
axes[2, 0].set_xticks(range(len(df['Year'])))
axes[2, 0].set_xticklabels(df['Year'], rotation=45)
axes[2, 0].set_yticks(range(len(df.columns[1:])))
axes[2, 0].set_yticklabels(df.columns[1:])
for i in range(len(df.columns[1:])):
    for j in range(len(df['Year'])):
        val = heatmap_data.iloc[i, j]
        if pd.notna(val):
            axes[2, 0].text(j, i, f'{val:.0f}', ha='center', va='center', color='black', fontsize=6)
plt.colorbar(im, ax=axes[2, 0])

# 6. Area Chart - Yearly Trend
axes[2, 1].fill_between(yearly_total.index, yearly_total.values, color='lightblue', alpha=0.7)
axes[2, 1].plot(yearly_total.index, yearly_total.values, color='blue', linewidth=2)
axes[2, 1].set_title("Yearly Ozone Area Chart")
axes[2, 1].set_xlabel("Year")
axes[2, 1].set_ylabel("Total Value")
axes[2, 1].grid(True)
for x, y in zip(yearly_total.index, yearly_total.values):
    axes[2, 1].annotate(f'{y:.0f}', (x, y), textcoords="offset points", xytext=(0,5), ha='center', fontsize=7)

plt.tight_layout()
plt.savefig('all_charts.png', dpi=300)
plt.show()

print("All charts displayed with data labels!")

