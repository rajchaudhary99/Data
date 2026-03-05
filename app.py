from flask import Flask, render_template, request
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from scipy import stats

app = Flask(__name__)

months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

df = pd.read_excel("Year_vs_Month_Monthly_Average_Ozone_Pivot_Rounded.xlsx")
df2 = pd.read_excel("Delhi_TOC.xlsx", skiprows=1)
df2.columns = ['Index', 'Year'] + months + ['Yearly_Avg', 'SD']
df2 = df2[['Year'] + months]

years = sorted(df['Year'].unique())

# Helper function to safely convert to float
def safe_float(val):
    try:
        if pd.isna(val) or val == '-' or val == '':
            return None  # Return None for missing values
        return float(val)
    except:
        return None

# Helper function to get value with year average fallback
def get_value_with_fallback(dataframe, year, month):
    """Get value for a specific year/month, fill missing with year average"""
    try:
        val = safe_float(dataframe[dataframe['Year'] == year][month].values[0])
        if val is not None:
            return val
        
        # Calculate year average from available months
        year_data = dataframe[dataframe['Year'] == year]
        if len(year_data) > 0:
            year_vals = [safe_float(year_data[m].values[0]) for m in months]
            year_vals = [v for v in year_vals if v is not None]  # Filter out None
            if year_vals:
                return np.mean(year_vals)
        return 0
    except:
        return 0

# Meteorological Seasons
seasons = {
    'Winter': ['Dec', 'Jan', 'Feb'],
    'Pre-monsoon': ['Feb', 'Mar', 'Apr', 'May', 'Jun'],
    'Monsoon': ['Jul', 'Aug', 'Sep'],
    'Post-monsoon': ['Oct', 'Nov']
}

# ML Analysis function
def generate_ml_insights(data1, data2, labels, data_type=""):
    """Generate ML-based insights in bullet point format"""
    insights = []
    
    # Linear regression for trend
    x = np.arange(len(data1))
    slope1, intercept1, r1, p1, se1 = stats.linregress(x, data1)
    slope2, intercept2, r2, p2, se2 = stats.linregress(x, data2)
    
    # Trend analysis
    trend1 = "increasing" if slope1 > 0 else "decreasing"
    trend2 = "increasing" if slope2 > 0 else "decreasing"
    insights.append(f"<strong>📈 Trend Analysis:</strong> OMI-satellite shows {trend1} trend ({abs(slope1):.3f} DU/{data_type}), Dobson shows {trend2} trend ({abs(slope2):.3f} DU/{data_type})")
    
    # Correlation
    corr, _ = stats.pearsonr(data1, data2)
    corr_strength = "strong" if abs(corr) > 0.7 else "moderate" if abs(corr) > 0.4 else "weak"
    insights.append(f"<strong>🔗 Correlation:</strong> {corr_strength.capitalize()} agreement (r={corr:.3f}) between measurement methods")
    
    # Statistical summary
    insights.append(f"<strong>📊 OMI-satellite:</strong> Mean={np.mean(data1):.2f} DU | Std={np.std(data1):.2f} DU | Range=[{np.min(data1):.2f}-{np.max(data1):.2f}] DU")
    insights.append(f"<strong>📊 Dobson:</strong> Mean={np.mean(data2):.2f} DU | Std={np.std(data2):.2f} DU | Range=[{np.min(data2):.2f}-{np.max(data2):.2f}] DU")
    
    # Difference analysis
    diff = np.mean(data1) - np.mean(data2)
    insights.append(f"<strong>⚖️ Difference:</strong> OMI-satellite is {'higher' if diff > 0 else 'lower'} by {abs(diff):.2f} DU ({abs(diff/np.mean(data2)*100):.2f}%) on average")
    
    # Variability comparison
    cv1 = (np.std(data1) / np.mean(data1)) * 100
    cv2 = (np.std(data2) / np.mean(data2)) * 100
    insights.append(f"<strong>📉 Variability:</strong> OMI CV={cv1:.2f}%, Dobson CV={cv2:.2f}% ({'OMI more stable' if cv1 < cv2 else 'Dobson more stable'})")
    
    return "<br>• " + "<br>• ".join(insights)

@app.route('/', methods=['GET', 'POST'])
def index():
    view_type = request.form.get('view_type', 'seasonal')
    
    charts_html = []
    insights_list = []
    
    if view_type == 'seasonal':
        # Create separate bar and trend charts for each season
        season_list = [('Winter', '🌨️'), ('Pre-monsoon', '☀️'), ('Monsoon', '🌧️'), ('Post-monsoon', '🍂')]
        
        for season_name, emoji in season_list:
            season_months = seasons.get(season_name, [])
            if not season_months:
                continue
            f1_seasonal, f2_seasonal, year_labels = [], [], []
            
            for year in years:
                vals_f1 = [get_value_with_fallback(df, year, m) for m in season_months]
                vals_f2 = [get_value_with_fallback(df2, year, m) for m in season_months]
                f1_seasonal.append(np.mean(vals_f1))
                f2_seasonal.append(np.mean(vals_f2))
                year_labels.append(str(year))
            
            # Bar Chart
            fig_bar = go.Figure()
            fig_bar.add_trace(go.Bar(x=year_labels, y=f1_seasonal, name='OMI-satellite Data', marker=dict(color='#ff6b6b', line=dict(color='white', width=2)), text=[f'{v:.2f}' for v in f1_seasonal], textposition='outside'))
            fig_bar.add_trace(go.Bar(x=year_labels, y=f2_seasonal, name='Dobson spectrophotometer', marker=dict(color='#4ecdc4', line=dict(color='white', width=2)), text=[f'{v:.2f}' for v in f2_seasonal], textposition='outside'))
            fig_bar.update_layout(
                title=f'{emoji} {season_name} Season - Bar Chart ({"-".join(season_months)})',
                barmode='group',
                height=450,
                plot_bgcolor='#f8fafc',
                paper_bgcolor='white',
                font=dict(family='Poppins', color='#1e293b', size=12),
                title_font=dict(size=18, color='#0f172a'),
                xaxis=dict(title=dict(text='Year →', font=dict(size=14, color='#0f172a', family='Poppins')), tickangle=-45, gridcolor='#e2e8f0', showgrid=True, showline=True, linewidth=2, linecolor='#1e293b'),
                yaxis=dict(title=dict(text='TCO Concentration (DU) ↑', font=dict(size=14, color='#0f172a', family='Poppins'), standoff=15), gridcolor='#e2e8f0', showline=True, linewidth=2, linecolor='#1e293b'),
                hovermode='x unified',
                margin=dict(l=80, r=40, t=80, b=80)
            )
            
            # Trend Chart
            fig_trend = go.Figure()
            fig_trend.add_trace(go.Scatter(x=year_labels, y=f1_seasonal, name='OMI-satellite', mode='lines+markers', line=dict(color='#ff6b6b', width=3), marker=dict(size=10)))
            fig_trend.add_trace(go.Scatter(x=year_labels, y=f2_seasonal, name='Dobson spectrophotometer', mode='lines+markers', line=dict(color='#4ecdc4', width=3), marker=dict(size=10)))
            fig_trend.update_layout(
                title=f'{emoji} {season_name} Season - Trend Analysis ({"-".join(season_months)})',
                height=450,
                plot_bgcolor='#f8fafc',
                paper_bgcolor='white',
                font=dict(family='Poppins', color='#1e293b', size=12),
                title_font=dict(size=18, color='#0f172a'),
                xaxis=dict(title=dict(text='Year →', font=dict(size=14, color='#0f172a', family='Poppins')), tickangle=-45, gridcolor='#e2e8f0', showgrid=True, showline=True, linewidth=2, linecolor='#1e293b'),
                yaxis=dict(title=dict(text='TCO Concentration (DU) ↑', font=dict(size=14, color='#0f172a', family='Poppins'), standoff=15), gridcolor='#e2e8f0', showline=True, linewidth=2, linecolor='#1e293b'),
                hovermode='x unified',
                margin=dict(l=80, r=40, t=80, b=80)
            )
            
            # Generate ML insights
            insights = generate_ml_insights(f1_seasonal, f2_seasonal, year_labels, "year")
            
            config = {'toImageButtonOptions': {'format': 'png', 'scale': 2}, 'displayModeBar': True, 'displaylogo': False}
            charts_html.append(fig_bar.to_html(full_html=False, config={**config, 'toImageButtonOptions': {**config['toImageButtonOptions'], 'filename': f'{season_name}_bar'}}))
            insights_list.append(insights)
            charts_html.append(fig_trend.to_html(full_html=False, config={**config, 'toImageButtonOptions': {**config['toImageButtonOptions'], 'filename': f'{season_name}_trend'}}))
            insights_list.append(insights)
    
    elif view_type == 'yearwise':
        # Year-wise Bar Chart
        f1_yearly, f2_yearly = [], []
        for year in years:
            vals_f1 = [get_value_with_fallback(df, year, m) for m in months]
            vals_f2 = [get_value_with_fallback(df2, year, m) for m in months]
            f1_yearly.append(np.mean(vals_f1))
            f2_yearly.append(np.mean(vals_f2))
        
        year_labels = [str(y) for y in years]
        
        # Bar Chart
        fig1 = go.Figure()
        fig1.add_trace(go.Bar(x=year_labels, y=f1_yearly, name='OMI-satellite Data', marker=dict(color='#ff6b6b', line=dict(color='white', width=2)), text=[f'{v:.2f}' for v in f1_yearly], textposition='outside'))
        fig1.add_trace(go.Bar(x=year_labels, y=f2_yearly, name='Dobson spectrophotometer', marker=dict(color='#4ecdc4', line=dict(color='white', width=2)), text=[f'{v:.2f}' for v in f2_yearly], textposition='outside'))
        fig1.update_layout(
            title='📊 Year-wise Average Ozone Analysis',
            barmode='group',
            height=450,
            plot_bgcolor='#f8fafc',
            paper_bgcolor='white',
            font=dict(family='Poppins', color='#1e293b', size=12),
            title_font=dict(size=18, color='#0f172a'),
            xaxis=dict(title=dict(text='Year →', font=dict(size=14, color='#0f172a', family='Poppins')), tickangle=-45, gridcolor='#e2e8f0', showgrid=True, showline=True, linewidth=2, linecolor='#1e293b'),
            yaxis=dict(title=dict(text='TCO Concentration (DU) ↑', font=dict(size=14, color='#0f172a', family='Poppins'), standoff=15), gridcolor='#e2e8f0', showline=True, linewidth=2, linecolor='#1e293b'),
            hovermode='x unified',
            margin=dict(l=80, r=40, t=80, b=80)
        )
        
        # Trend Chart
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=year_labels, y=f1_yearly, name='OMI-satellite', mode='lines+markers', line=dict(color='#ff6b6b', width=3), marker=dict(size=10)))
        fig2.add_trace(go.Scatter(x=year_labels, y=f2_yearly, name='Dobson spectrophotometer', mode='lines+markers', line=dict(color='#4ecdc4', width=3), marker=dict(size=10)))
        fig2.update_layout(
            title='📈 Year-wise Trend Analysis',
            height=450,
            plot_bgcolor='#f8fafc',
            paper_bgcolor='white',
            font=dict(family='Poppins', color='#1e293b', size=12),
            title_font=dict(size=18, color='#0f172a'),
            xaxis=dict(title=dict(text='Year →', font=dict(size=14, color='#0f172a', family='Poppins')), tickangle=-45, gridcolor='#e2e8f0', showgrid=True, showline=True, linewidth=2, linecolor='#1e293b'),
            yaxis=dict(title=dict(text='TCO Concentration (DU) ↑', font=dict(size=14, color='#0f172a', family='Poppins'), standoff=15), gridcolor='#e2e8f0', showline=True, linewidth=2, linecolor='#1e293b'),
            hovermode='x unified',
            margin=dict(l=80, r=40, t=80, b=80)
        )
        
        # Generate ML insights
        insights = generate_ml_insights(f1_yearly, f2_yearly, year_labels, "year")
        
        config = {'toImageButtonOptions': {'format': 'png', 'scale': 2}, 'displayModeBar': True, 'displaylogo': False}
        charts_html.append(fig1.to_html(full_html=False, config={**config, 'toImageButtonOptions': {**config['toImageButtonOptions'], 'filename': 'yearwise_bar'}}))
        insights_list.append(insights)
        charts_html.append(fig2.to_html(full_html=False, config={**config, 'toImageButtonOptions': {**config['toImageButtonOptions'], 'filename': 'yearwise_trend'}}))
        insights_list.append(insights)
    
    elif view_type == 'monthwise':
        # Month-wise Average with year range
        year_range = f"{min(years)} - {max(years)}"
        month_labels = [f"{m}({year_range})" for m in months]
        f1_monthly, f2_monthly = [], []
        for month in months:
            vals_f1 = [get_value_with_fallback(df, year, month) for year in years]
            vals_f2 = [get_value_with_fallback(df2, year, month) for year in years]
            f1_monthly.append(np.mean(vals_f1))
            f2_monthly.append(np.mean(vals_f2))
        
        # Bar Chart
        fig1 = go.Figure()
        fig1.add_trace(go.Bar(x=month_labels, y=f1_monthly, name='OMI-satellite Data', marker=dict(color='#ff6b6b', line=dict(color='white', width=2)), text=[f'{v:.2f}' for v in f1_monthly], textposition='outside'))
        fig1.add_trace(go.Bar(x=month_labels, y=f2_monthly, name='Dobson spectrophotometer', marker=dict(color='#4ecdc4', line=dict(color='white', width=2)), text=[f'{v:.2f}' for v in f2_monthly], textposition='outside'))
        fig1.update_layout(
            title=f'📊 Month-wise Average Ozone Analysis ({year_range})',
            barmode='group',
            height=450,
            plot_bgcolor='#f8fafc',
            paper_bgcolor='white',
            font=dict(family='Poppins', color='#1e293b', size=12),
            title_font=dict(size=18, color='#0f172a'),
            xaxis=dict(title=dict(text='Month (2004 - 2025) →', font=dict(size=14, color='#0f172a', family='Poppins')), gridcolor='#e2e8f0', showgrid=True, showline=True, linewidth=2, linecolor='#1e293b'),
            yaxis=dict(title=dict(text='TCO Concentration (DU) ↑', font=dict(size=14, color='#0f172a', family='Poppins'), standoff=15), gridcolor='#e2e8f0', showline=True, linewidth=2, linecolor='#1e293b'),
            hovermode='x unified',
            margin=dict(l=80, r=40, t=80, b=80)
        )
        
        # Trend Chart
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=month_labels, y=f1_monthly, name='OMI-satellite', mode='lines+markers', line=dict(color='#ff6b6b', width=4, shape='spline'), marker=dict(size=12)))
        fig2.add_trace(go.Scatter(x=month_labels, y=f2_monthly, name='Dobson spectrophotometer', mode='lines+markers', line=dict(color='#4ecdc4', width=4, shape='spline'), marker=dict(size=12)))
        fig2.update_layout(
            title=f'📈 Month-wise Trend Analysis ({year_range})',
            height=450,
            plot_bgcolor='#f8fafc',
            paper_bgcolor='white',
            font=dict(family='Poppins', color='#1e293b', size=12),
            title_font=dict(size=18, color='#0f172a'),
            xaxis=dict(title=dict(text='Month (2004 - 2025) →', font=dict(size=14, color='#0f172a', family='Poppins')), gridcolor='#e2e8f0', showgrid=True, showline=True, linewidth=2, linecolor='#1e293b'),
            yaxis=dict(title=dict(text='TCO Concentration (DU) ↑', font=dict(size=14, color='#0f172a', family='Poppins'), standoff=15), gridcolor='#e2e8f0', showline=True, linewidth=2, linecolor='#1e293b'),
            hovermode='x unified',
            margin=dict(l=80, r=40, t=80, b=80)
        )
        
        # Generate ML insights
        insights = generate_ml_insights(f1_monthly, f2_monthly, months, "month")
        
        config = {'toImageButtonOptions': {'format': 'png', 'scale': 2}, 'displayModeBar': True, 'displaylogo': False}
        charts_html.append(fig1.to_html(full_html=False, config={**config, 'toImageButtonOptions': {**config['toImageButtonOptions'], 'filename': 'monthwise_bar'}}))
        insights_list.append(insights)
        charts_html.append(fig2.to_html(full_html=False, config={**config, 'toImageButtonOptions': {**config['toImageButtonOptions'], 'filename': 'monthwise_trend'}}))
        insights_list.append(insights)
    
    return render_template('index.html', charts_html=charts_html, insights_list=insights_list, selected=view_type, years=years, months=months)

if __name__ == '__main__':
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    app.run(debug=True, port=5001)
