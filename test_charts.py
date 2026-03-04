import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Load data
df = pd.read_excel("Year_vs_Month_Monthly_Average_Ozone_Pivot_Rounded.xlsx")

# Get sample values
val1 = df[df['Year'] == 2004]['Jan'].values[0]
val2 = df[df['Year'] == 2005]['Feb'].values[0]

print(f"Creating comparison charts for Jan 2004 ({val1}) vs Feb 2005 ({val2})")

# Create 2x2 subplot
fig = make_subplots(
    rows=2, cols=2,
    subplot_titles=('Biaxial Bar Chart', 'Line + Bar + Area Composed', 'Gradient Pie Chart', 'Comparison Overview'),
    specs=[[{'secondary_y': True}, {'type': 'xy'}], 
           [{'type': 'domain'}, {'type': 'xy'}]]
)

# 1. Biaxial Bar Chart
fig.add_trace(go.Bar(name='Period 1', x=['Jan 2004'], y=[val1], 
                     marker_color='#FF6B6B', text=[val1], textposition='outside'), 
              row=1, col=1, secondary_y=False)
fig.add_trace(go.Bar(name='Period 2', x=['Feb 2005'], y=[val2], 
                     marker_color='#4ECDC4', text=[val2], textposition='outside'), 
              row=1, col=1, secondary_y=True)

# 2. Line + Bar + Area Composed
categories = ['Jan 2004', 'Feb 2005']
fig.add_trace(go.Bar(name='Bar', x=categories, y=[val1, val2], 
                     marker_color='rgba(255, 107, 107, 0.6)'), row=1, col=2)
fig.add_trace(go.Scatter(name='Line', x=categories, y=[val1, val2], 
                         mode='lines+markers', line=dict(color='#45B7D1', width=3), 
                         marker=dict(size=12)), row=1, col=2)
fig.add_trace(go.Scatter(name='Area', x=categories, y=[val1*0.9, val2*0.9], 
                         fill='tozeroy', fillcolor='rgba(152, 216, 200, 0.3)', 
                         line=dict(color='rgba(152, 216, 200, 0)'), showlegend=False), row=1, col=2)

# 3. Gradient Pie Chart
fig.add_trace(go.Pie(labels=['Jan 2004', 'Feb 2005'], 
                     values=[val1, val2],
                     marker=dict(colors=['#FF6B6B', '#4ECDC4'],
                               line=dict(color='white', width=2)),
                     textinfo='label+percent+value',
                     hole=0.4), row=2, col=1)

# 4. Comparison Overview
fig.add_trace(go.Bar(name='Value', x=['Jan\n2004', 'Feb\n2005'], 
                     y=[val1, val2], text=[val1, val2], textposition='outside',
                     marker=dict(color=[val1, val2], 
                               colorscale='Viridis',
                               showscale=True,
                               colorbar=dict(x=1.15))), row=2, col=2)

fig.update_yaxes(title_text="Period 1 Value", row=1, col=1, secondary_y=False)
fig.update_yaxes(title_text="Period 2 Value", row=1, col=1, secondary_y=True)
fig.update_layout(height=800, title_text='Advanced Comparison Test', 
                 showlegend=True, legend=dict(x=0.01, y=0.99))

# Save and show
fig.write_html('test_advanced_charts.html')
print("Charts saved to test_advanced_charts.html")
print("Open this file in your browser to see the 4 advanced charts!")
