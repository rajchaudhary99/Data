from flask import Flask, render_template, request
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

app = Flask(__name__)

months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

df = pd.read_excel("Year_vs_Month_Monthly_Average_Ozone_Pivot_Rounded.xlsx")
df2 = pd.read_excel("Delhi_TOC.xlsx", skiprows=1)
df2.columns = ['Index', 'Year'] + months + ['Yearly_Avg', 'SD']
df2 = df2[['Year'] + months]

years = sorted(df['Year'].unique())

@app.route('/', methods=['GET', 'POST'])
def index():
    view_type = request.form.get('view_type', 'custom')
    
    if view_type == 'file_compare':
        selected_year = int(request.form.get('compare_year', years[0]))
        selected_month = request.form.get('compare_month', 'Jan')
        
        # Get values from both files
        val_file1 = df[df['Year'] == selected_year][selected_month].values[0] if len(df[df['Year'] == selected_year]) > 0 else 0
        val_file2 = df2[df2['Year'] == selected_year][selected_month].values[0] if len(df2[df2['Year'] == selected_year]) > 0 else 0
        
        diff = val_file2 - val_file1
        pct_change = ((val_file2 - val_file1) / val_file1 * 100) if val_file1 != 0 else 0
        
        # Get all months data for both files
        file1_data = []
        file2_data = []
        for month in months:
            v1 = df[df['Year'] == selected_year][month].values[0] if len(df[df['Year'] == selected_year]) > 0 else 0
            v2 = df2[df2['Year'] == selected_year][month].values[0] if len(df2[df2['Year'] == selected_year]) > 0 else 0
            file1_data.append(v1)
            file2_data.append(v2)
        
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                f'📊 Grouped Bar - {selected_year}',
                f'📈 Line Comparison - {selected_year}',
                f'🎯 {selected_month} {selected_year} Comparison',
                '📊 Correlation Scatter'
            ),
            specs=[
                [{'type': 'xy'}, {'type': 'xy'}],
                [{'type': 'indicator'}, {'type': 'xy'}]
            ],
            vertical_spacing=0.15,
            horizontal_spacing=0.12
        )
        
        # 1. Grouped Bar Chart
        fig.add_trace(go.Bar(
            x=months,
            y=file1_data,
            name='File 1 (Ozone)',
            marker=dict(color='#ff6b6b', line=dict(color='white', width=2)),
            text=[f'{v:.1f}' for v in file1_data],
            textposition='outside',
            textfont=dict(size=10, family='Inter')
        ), row=1, col=1)
        
        fig.add_trace(go.Bar(
            x=months,
            y=file2_data,
            name='File 2 (Delhi TOC)',
            marker=dict(color='#4ecdc4', line=dict(color='white', width=2)),
            text=[f'{v:.1f}' for v in file2_data],
            textposition='outside',
            textfont=dict(size=10, family='Inter')
        ), row=1, col=1)
        
        # 2. Line Chart Comparison
        fig.add_trace(go.Scatter(
            x=months,
            y=file1_data,
            name='File 1 (Ozone)',
            mode='lines+markers',
            line=dict(color='#ff6b6b', width=3, shape='spline'),
            marker=dict(size=10, line=dict(color='white', width=2))
        ), row=1, col=2)
        
        fig.add_trace(go.Scatter(
            x=months,
            y=file2_data,
            name='File 2 (Delhi TOC)',
            mode='lines+markers',
            line=dict(color='#4ecdc4', width=3, shape='spline'),
            marker=dict(size=10, line=dict(color='white', width=2))
        ), row=1, col=2)
        
        # 3. Indicator for selected month
        fig.add_trace(go.Indicator(
            mode='number+delta',
            value=val_file2,
            delta={'reference': val_file1, 'increasing': {'color': '#43e97b'}, 'decreasing': {'color': '#ff6b6b'}, 'font': {'size': 20}},
            title={'text': f'<b>File 2 vs File 1</b><br><span style="font-size:14px">{selected_month} {selected_year}</span>', 'font': {'size': 18, 'family': 'Inter'}},
            number={'font': {'size': 40, 'family': 'Inter', 'color': '#4ecdc4'}},
            domain={'x': [0, 0.45], 'y': [0, 0.45]}
        ), row=2, col=1)
        
        # 4. Scatter Plot - Correlation
        fig.add_trace(go.Scatter(
            x=file1_data,
            y=file2_data,
            mode='markers+text',
            text=months,
            textposition='top center',
            textfont=dict(size=10, family='Inter'),
            marker=dict(
                size=12,
                color=list(range(12)),
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title='Month', x=1.15),
                line=dict(color='white', width=2)
            ),
            name='Correlation',
            showlegend=False
        ), row=2, col=2)
        
        # Add diagonal reference line
        max_val = max(max(file1_data), max(file2_data))
        fig.add_trace(go.Scatter(
            x=[0, max_val],
            y=[0, max_val],
            mode='lines',
            line=dict(color='gray', width=2, dash='dash'),
            name='1:1 Line',
            showlegend=False
        ), row=2, col=2)
        
        fig.update_xaxes(showgrid=True, gridcolor='rgba(0,0,0,0.05)', tickfont=dict(size=11, family='Inter'))
        fig.update_yaxes(showgrid=True, gridcolor='rgba(0,0,0,0.05)', tickfont=dict(size=11, family='Inter'))
        fig.update_xaxes(title_text='File 1 (Ozone)', row=2, col=2)
        fig.update_yaxes(title_text='File 2 (Delhi TOC)', row=2, col=2)
        
        fig.update_layout(
            height=900,
            title=dict(
                text=f'📊 File Comparison Dashboard - Year {selected_year}',
                font=dict(size=28, color='#2d3748', family='Inter', weight=700),
                x=0.5,
                xanchor='center'
            ),
            showlegend=True,
            legend=dict(
                x=0.01, y=0.99,
                bgcolor='rgba(255,255,255,0.95)',
                bordercolor='rgba(102, 126, 234, 0.3)',
                borderwidth=2,
                font=dict(size=12, family='Inter')
            ),
            plot_bgcolor='rgba(248, 250, 252, 0.5)',
            paper_bgcolor='white',
            font=dict(family='Inter', size=12, color='#2d3748'),
            margin=dict(t=100, b=60, l=60, r=120)
        )
    
    elif view_type == 'custom':
        selected_months = request.form.getlist('months')
        selected_years = request.form.getlist('years')
        
        if not selected_months:
            selected_months = months
        if not selected_years:
            selected_years = [str(years[0])]
        
        # Get data from both files
        file1_all = []
        file2_all = []
        labels = []
        
        for month in selected_months:
            for year in selected_years:
                v1 = df[df['Year'] == int(year)][month].values[0] if len(df[df['Year'] == int(year)]) > 0 else 0
                v2 = df2[df2['Year'] == int(year)][month].values[0] if len(df2[df2['Year'] == int(year)]) > 0 else 0
                file1_all.append(v1)
                file2_all.append(v2)
                labels.append(f'{year} {month}')
        
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('📊 Grouped Bar Comparison', '📈 Line Trend Comparison', '🎯 Violin Distribution', '📊 Scatter Correlation'),
            specs=[[{'type': 'xy'}, {'type': 'xy'}], [{'type': 'xy'}, {'type': 'xy'}]],
            vertical_spacing=0.15,
            horizontal_spacing=0.12
        )
        
        # 1. Grouped Bar Chart
        fig.add_trace(go.Bar(
            x=labels, y=file1_all,
            name='File 1 (Ozone)',
            marker=dict(color='#ff6b6b', line=dict(color='white', width=2)),
            text=[f'{v:.1f}' for v in file1_all],
            textposition='outside',
            textfont=dict(size=9, family='Inter')
        ), row=1, col=1)
        
        fig.add_trace(go.Bar(
            x=labels, y=file2_all,
            name='File 2 (Delhi TOC)',
            marker=dict(color='#4ecdc4', line=dict(color='white', width=2)),
            text=[f'{v:.1f}' for v in file2_all],
            textposition='outside',
            textfont=dict(size=9, family='Inter')
        ), row=1, col=1)
        
        # 2. Line Chart
        fig.add_trace(go.Scatter(
            x=labels, y=file1_all,
            name='File 1 (Ozone)',
            mode='lines+markers',
            line=dict(color='#ff6b6b', width=3),
            marker=dict(size=8, line=dict(color='white', width=2))
        ), row=1, col=2)
        
        fig.add_trace(go.Scatter(
            x=labels, y=file2_all,
            name='File 2 (Delhi TOC)',
            mode='lines+markers',
            line=dict(color='#4ecdc4', width=3),
            marker=dict(size=8, line=dict(color='white', width=2))
        ), row=1, col=2)
        
        # 3. Violin Plot
        fig.add_trace(go.Violin(
            y=file1_all,
            name='File 1 (Ozone)',
            box_visible=True,
            meanline_visible=True,
            fillcolor='#ff6b6b',
            opacity=0.6,
            line=dict(color='#ff6b6b')
        ), row=2, col=1)
        
        fig.add_trace(go.Violin(
            y=file2_all,
            name='File 2 (Delhi TOC)',
            box_visible=True,
            meanline_visible=True,
            fillcolor='#4ecdc4',
            opacity=0.6,
            line=dict(color='#4ecdc4')
        ), row=2, col=1)
        
        # 4. Scatter Correlation
        fig.add_trace(go.Scatter(
            x=file1_all, y=file2_all,
            mode='markers',
            marker=dict(size=10, color='#667eea', line=dict(color='white', width=2)),
            name='Correlation',
            showlegend=False
        ), row=2, col=2)
        
        max_val = max(max(file1_all), max(file2_all))
        fig.add_trace(go.Scatter(
            x=[0, max_val], y=[0, max_val],
            mode='lines',
            line=dict(color='gray', width=2, dash='dash'),
            showlegend=False
        ), row=2, col=2)
        
        fig.update_xaxes(tickangle=-45, showgrid=True, gridcolor='rgba(0,0,0,0.05)', tickfont=dict(size=10, family='Inter'))
        fig.update_yaxes(showgrid=True, gridcolor='rgba(0,0,0,0.05)', tickfont=dict(size=11, family='Inter'))
        fig.update_xaxes(title_text='File 1 (Ozone)', row=2, col=2)
        fig.update_yaxes(title_text='File 2 (Delhi TOC)', row=2, col=2)
        
        fig.update_layout(
            height=900,
            title=dict(
                text=f'🎯 Custom File Comparison - {len(selected_years)} Year(s) × {len(selected_months)} Month(s)',
                font=dict(size=28, color='#2d3748', family='Inter', weight=700),
                x=0.5, xanchor='center'
            ),
            showlegend=True,
            legend=dict(x=0.01, y=0.99, bgcolor='rgba(255,255,255,0.95)', bordercolor='rgba(102, 126, 234, 0.3)', borderwidth=2, font=dict(size=12, family='Inter')),
            plot_bgcolor='rgba(248, 250, 252, 0.5)',
            paper_bgcolor='white',
            font=dict(family='Inter', size=12, color='#2d3748'),
            margin=dict(t=100, b=60, l=60, r=120)
        )elected_months:
                val = df[df['Year'] == int(year)][month].values[0] if len(df[df['Year'] == int(year)]) > 0 else 0
                year_values.append(val)
            year_values.append(year_values[0])  # Close the radar
            
            fig.add_trace(go.Scatterpolar(
                r=year_values,
                theta=selected_months + [selected_months[0]],
                name=f'{year}',
                fill='toself',
                fillcolor=radar_colors[idx % len(radar_colors)],
                opacity=0.4,
                line=dict(color=radar_colors[idx % len(radar_colors)], width=3),
                hovertemplate='<b>Year %{fullData.name}</b><br>%{theta}: %{r:.2f}<extra></extra>'
            ), row=2, col=1)
        
        # 3. Area Chart - Shows cumulative trends over time
        area_colors = ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#43e97b', '#fa709a']
        for idx, year in enumerate(selected_years):
            year_values = []
            for month in selected_months:
                val = df[df['Year'] == int(year)][month].values[0] if len(df[df['Year'] == int(year)]) > 0 else 0
                year_values.append(val)
            
            fig.add_trace(go.Scatter(
                x=selected_months,
                y=year_values,
                name=f'{year}',
                mode='lines',
                fill='tonexty' if idx > 0 else 'tozeroy',
                fillcolor=area_colors[idx % len(area_colors)],
                opacity=0.5,
                line=dict(color=area_colors[idx % len(area_colors)], width=3, shape='spline'),
                hovertemplate='<b>Year %{fullData.name}</b><br>%{x}: %{y:.2f}<extra></extra>'
            ), row=3, col=1)
        
        # 4. Funnel Chart - Shows value hierarchy (sorted descending)
        sorted_data = sorted(zip(labels, values), key=lambda x: x[1], reverse=True)
        funnel_labels = [x[0] for x in sorted_data]
        funnel_values = [x[1] for x in sorted_data]
        
        fig.add_trace(go.Funnel(
            y=funnel_labels,
            x=funnel_values,
            textposition='inside',
            textinfo='value+percent initial',
            textfont=dict(size=10, family='Inter', color='white'),
            marker=dict(
                color=['#667eea', '#764ba2', '#f093fb', '#4facfe', '#43e97b', '#fa709a'] * (len(funnel_values) // 6 + 1),
                line=dict(color='white', width=2)
            ),
            hovertemplate='<b>%{y}</b><br>Value: %{x:.2f}<extra></extra>'
        ), row=4, col=1)
        
        fig.update_xaxes(showgrid=False, tickfont=dict(size=11, family='Inter'))
        fig.update_xaxes(row=3, col=1, showgrid=True, gridcolor='rgba(0,0,0,0.05)', tickfont=dict(size=11, family='Inter'))
        fig.update_yaxes(showgrid=True, gridcolor='rgba(0,0,0,0.05)', tickfont=dict(size=11, family='Inter'))
        
        fig.update_layout(
            height=1800, 
            showlegend=True,
            legend=dict(
                x=1.02, y=0.75, 
                bgcolor='rgba(255,255,255,0.95)', 
                bordercolor='rgba(102, 126, 234, 0.3)', 
                borderwidth=2,
                font=dict(size=12, family='Inter')
            ),
            title=dict(
                text=f'🎯 Advanced Analytics - {len(selected_years)} Year(s) × {len(selected_months)} Month(s)', 
                font=dict(size=24, color='#2d3748', family='Inter', weight=700),
                x=0.5,
                xanchor='center'
            ),
            plot_bgcolor='rgba(248, 250, 252, 0.5)',
            paper_bgcolor='white',
            font=dict(family='Inter', size=12, color='#2d3748'),
            margin=dict(t=80, b=60, l=60, r=120)
        )
    
    elif view_type == 'compare':
        year1 = request.form.get('year1', years[0])
        month1 = request.form.get('month1', 'Jan')
        year2 = request.form.get('year2', years[1] if len(years) > 1 else years[0])
        month2 = request.form.get('month2', 'Feb')
        
        val1 = df[df['Year'] == int(year1)][month1].values[0] if len(df[df['Year'] == int(year1)]) > 0 else 0
        val2 = df[df['Year'] == int(year2)][month2].values[0] if len(df[df['Year'] == int(year2)]) > 0 else 0
        diff = val2 - val1
        pct_change = ((val2 - val1) / val1 * 100) if val1 != 0 else 0
        
        # Create metric cards data
        fig = go.Figure()
        
        # Create a dashboard with 4 subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                '📈 Comparison Overview',
                '🎯 Performance Gauge',
                '📊 Trend Analysis',
                '📊 Value Distribution'
            ),
            specs=[
                [{'type': 'indicator'}, {'type': 'indicator'}],
                [{'type': 'xy'}, {'type': 'domain'}]
            ],
            vertical_spacing=0.15,
            horizontal_spacing=0.12
        )

        # 1. Period 1 Indicator Card
        fig.add_trace(go.Indicator(
            mode='number+delta',
            value=val1,
            title={'text': f'<b>{month1} {year1}</b><br><span style="font-size:14px;color:#999">Period 1</span>', 'font': {'size': 20, 'family': 'Inter'}},
            number={'font': {'size': 50, 'family': 'Inter', 'color': '#ff6b6b'}, 'suffix': ''},
            domain={'x': [0, 0.45], 'y': [0.55, 1]}
        ), row=1, col=1)

        # 2. Period 2 Indicator Card with Delta
        fig.add_trace(go.Indicator(
            mode='number+delta',
            value=val2,
            delta={'reference': val1, 'increasing': {'color': '#43e97b'}, 'decreasing': {'color': '#ff6b6b'}, 'font': {'size': 24}},
            title={'text': f'<b>{month2} {year2}</b><br><span style="font-size:14px;color:#999">Period 2 vs Period 1</span>', 'font': {'size': 20, 'family': 'Inter'}},
            number={'font': {'size': 50, 'family': 'Inter', 'color': '#4ecdc4'}},
            domain={'x': [0.55, 1], 'y': [0.55, 1]}
        ), row=1, col=2)

        # 3. Grouped Bar Chart with Line
        categories = ['Period 1', 'Period 2']
        fig.add_trace(go.Bar(
            x=categories,
            y=[val1, val2],
            name='Ozone Value',
            text=[f'{val1:.2f}', f'{val2:.2f}'],
            textposition='outside',
            textfont=dict(size=16, family='Inter', weight='bold'),
            marker=dict(
                color=['#ff6b6b', '#4ecdc4'],
                line=dict(color='white', width=3),
                pattern_shape=['', '/']
            ),
            hovertemplate='<b>%{x}</b><br>Value: %{y:.2f}<extra></extra>'
        ), row=2, col=1)
        
        # Add average line
        avg_val = (val1 + val2) / 2
        fig.add_trace(go.Scatter(
            x=categories,
            y=[avg_val, avg_val],
            mode='lines',
            name='Average',
            line=dict(color='#667eea', width=3, dash='dash'),
            hovertemplate='<b>Average</b><br>Value: %{y:.2f}<extra></extra>'
        ), row=2, col=1)
        
        # Add change annotation
        fig.add_annotation(
            x=0.5, y=max(val1, val2) * 1.1,
            text=f"<b>{'↑' if diff > 0 else '↓'} {abs(diff):.2f} ({abs(pct_change):.1f}%)</b>",
            showarrow=True,
            arrowhead=2,
            arrowsize=1,
            arrowwidth=2,
            arrowcolor='#43e97b' if diff > 0 else '#ff6b6b',
            font=dict(size=16, color='#43e97b' if diff > 0 else '#ff6b6b', family='Inter'),
            xref='x3', yref='y3',
            ax=0, ay=-40
        )

        # 4. Donut Chart - Proportion
        fig.add_trace(go.Pie(
            labels=[f'{month1} {year1}', f'{month2} {year2}'],
            values=[val1, val2],
            hole=0.6,
            marker=dict(
                colors=['#ff6b6b', '#4ecdc4'],
                line=dict(color='white', width=3)
            ),
            textinfo='label+percent',
            textfont=dict(size=13, family='Inter', weight='bold'),
            hovertemplate='<b>%{label}</b><br>Value: %{value:.2f}<br>Percent: %{percent}<extra></extra>'
        ), row=2, col=2)
        
        # Add center text for donut
        fig.add_annotation(
            text=f'<b>Total</b><br>{val1 + val2:.2f}',
            x=0.775, y=0.22,
            font=dict(size=18, family='Inter', color='#2d3748'),
            showarrow=False,
            xref='paper', yref='paper'
        )
        
        fig.update_xaxes(showgrid=False, tickfont=dict(size=13, family='Inter'), row=2, col=1)
        fig.update_yaxes(showgrid=True, gridcolor='rgba(0,0,0,0.05)', tickfont=dict(size=13, family='Inter'), row=2, col=1)
        
        fig.update_layout(
            height=900,
            title=dict(
                text=f'🔬 Period Comparison Dashboard: {month1} {year1} ↔ {month2} {year2}',
                font=dict(size=32, color='#2d3748', family='Inter', weight=700),
                x=0.5,
                xanchor='center',
                y=0.98
            ),
            showlegend=True,
            legend=dict(
                x=0.4, y=0.45,
                bgcolor='rgba(255,255,255,0.95)',
                bordercolor='rgba(102, 126, 234, 0.3)',
                borderwidth=2,
                font=dict(size=12, family='Inter')
            ),
            plot_bgcolor='rgba(248, 250, 252, 0.5)',
            paper_bgcolor='white',
            font=dict(family='Inter', size=12, color='#2d3748'),
            margin=dict(t=120, b=60, l=60, r=60)
        )
    
    elif view_type == 'quarter':
        quarter = request.form.get('quarter', 'Q1')
        selected_year = int(request.form.get('quarter_year', years[0]))
        
        q_months = {'Q1': ['Jan', 'Feb', 'Mar'], 'Q2': ['Apr', 'May', 'Jun'], 
                    'Q3': ['Jul', 'Aug', 'Sep'], 'Q4': ['Oct', 'Nov', 'Dec']}
        
        q_data = df[df['Year'] == selected_year][q_months[quarter]].values[0] if len(df[df['Year'] == selected_year]) > 0 else [0,0,0]
        
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('📊 Bar Chart', '📈 Line Chart'),
            specs=[[{'type': 'xy'}], [{'type': 'xy'}]],
            vertical_spacing=0.15,
            row_heights=[0.5, 0.5]
        )
        
        fig.add_trace(go.Bar(
            x=q_months[quarter], y=q_data, 
            text=[f'{v:.1f}' for v in q_data], 
            textposition='outside',
            textfont=dict(size=13, color='#2d3748', family='Inter'),
            marker=dict(color='#667eea', line=dict(color='white', width=2)),
            hovertemplate='<b>%{x}</b><br>Value: %{y:.2f}<extra></extra>'
        ), row=1, col=1)
        
        fig.add_trace(go.Scatter(
            x=q_months[quarter], y=q_data, 
            mode='lines+markers',
            marker=dict(size=14, color='#764ba2', line=dict(color='white', width=3)),
            line=dict(color='#764ba2', width=4, shape='spline'),
            hovertemplate='<b>%{x}</b><br>Value: %{y:.2f}<extra></extra>'
        ), row=2, col=1)
        
        fig.update_xaxes(showgrid=False, tickfont=dict(size=12, family='Inter'))
        fig.update_yaxes(showgrid=True, gridcolor='rgba(0,0,0,0.05)', tickfont=dict(size=12, family='Inter'))
        
        fig.update_layout(
            height=900, 
            showlegend=False,
            title=dict(
                text=f'📅 {quarter} {selected_year} - Quarterly Analysis',
                font=dict(size=24, color='#2d3748', family='Inter', weight=700),
                x=0.5,
                xanchor='center'
            ),
            plot_bgcolor='rgba(248, 250, 252, 0.5)',
            paper_bgcolor='white',
            font=dict(family='Inter', size=12, color='#2d3748'),
            margin=dict(t=80, b=60, l=60, r=60)
        )
    
    elif view_type == 'quarter_compare':
        year1 = int(request.form.get('quarter_year1', years[0]))
        year2 = int(request.form.get('quarter_year2', years[1] if len(years) > 1 else years[0]))
        selected_quarter = request.form.get('selected_quarter', 'all')
        
        q_months = {'Q1': ['Jan', 'Feb', 'Mar'], 'Q2': ['Apr', 'May', 'Jun'], 
                    'Q3': ['Jul', 'Aug', 'Sep'], 'Q4': ['Oct', 'Nov', 'Dec']}
        
        if selected_quarter == 'all':
            quarters = ['Q1', 'Q2', 'Q3', 'Q4']
            year1_data = []
            year2_data = []
            
            for quarter in quarters:
                q_vals1 = df[df['Year'] == year1][q_months[quarter]].values[0] if len(df[df['Year'] == year1]) > 0 else [0,0,0]
                q_vals2 = df[df['Year'] == year2][q_months[quarter]].values[0] if len(df[df['Year'] == year2]) > 0 else [0,0,0]
                year1_data.append(sum(q_vals1) / 3)
                year2_data.append(sum(q_vals2) / 3)
            
            title_text = f'📊 All Quarters Comparison: {year1} vs {year2}'
        else:
            quarters = [selected_quarter]
            q_vals1 = df[df['Year'] == year1][q_months[selected_quarter]].values[0] if len(df[df['Year'] == year1]) > 0 else [0,0,0]
            q_vals2 = df[df['Year'] == year2][q_months[selected_quarter]].values[0] if len(df[df['Year'] == year2]) > 0 else [0,0,0]
            year1_data = q_vals1
            year2_data = q_vals2
            quarters = q_months[selected_quarter]
            
            title_text = f'📊 {selected_quarter} Comparison: {year1} vs {year2}'
        
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=('📊 Comparison Chart', '🎯 Radar Comparison', '📈 Trend Analysis', '📊 Performance Gap', '🔥 Heatmap Analysis', '📉 Box Plot Distribution'),
            specs=[[{'type': 'xy'}, {'type': 'polar'}], [{'type': 'xy'}, {'type': 'xy'}], [{'type': 'xy'}, {'type': 'xy'}]],
            vertical_spacing=0.12,
            horizontal_spacing=0.12
        )
        
        # 1. Grouped Bar Chart
        fig.add_trace(go.Bar(
            x=quarters, y=year1_data, name=f'{year1}',
            marker=dict(color='#ff6b6b', line=dict(color='white', width=2)),
            text=[f'{v:.1f}' for v in year1_data],
            textposition='outside',
            hovertemplate=f'<b>{year1} %{{x}}</b><br>Value: %{{y:.2f}}<extra></extra>'
        ), row=1, col=1)
        
        fig.add_trace(go.Bar(
            x=quarters, y=year2_data, name=f'{year2}',
            marker=dict(color='#4ecdc4', line=dict(color='white', width=2)),
            text=[f'{v:.1f}' for v in year2_data],
            textposition='outside',
            hovertemplate=f'<b>{year2} %{{x}}</b><br>Value: %{{y:.2f}}<extra></extra>'
        ), row=1, col=1)
        
        # 2. Radar Chart
        fig.add_trace(go.Scatterpolar(
            r=year1_data + [year1_data[0]], theta=quarters + [quarters[0]],
            name=f'{year1}', fill='toself', fillcolor='rgba(255, 107, 107, 0.3)',
            line=dict(color='#ff6b6b', width=3)
        ), row=1, col=2)
        
        fig.add_trace(go.Scatterpolar(
            r=year2_data + [year2_data[0]], theta=quarters + [quarters[0]],
            name=f'{year2}', fill='toself', fillcolor='rgba(78, 205, 196, 0.3)',
            line=dict(color='#4ecdc4', width=3)
        ), row=1, col=2)
        
        # 3. Line Chart Trend
        fig.add_trace(go.Scatter(
            x=quarters, y=year1_data, name=f'{year1}',
            mode='lines+markers', line=dict(color='#ff6b6b', width=4),
            marker=dict(size=12, color='#ff6b6b', line=dict(color='white', width=2))
        ), row=2, col=1)
        
        fig.add_trace(go.Scatter(
            x=quarters, y=year2_data, name=f'{year2}',
            mode='lines+markers', line=dict(color='#4ecdc4', width=4),
            marker=dict(size=12, color='#4ecdc4', line=dict(color='white', width=2))
        ), row=2, col=1)
        
        # 4. Difference Chart
        differences = [y2 - y1 for y1, y2 in zip(year1_data, year2_data)]
        colors = ['#43e97b' if d > 0 else '#ff6b6b' for d in differences]
        
        fig.add_trace(go.Bar(
            x=quarters, y=differences, name='Difference',
            marker=dict(color=colors, line=dict(color='white', width=2)),
            text=[f'{d:+.1f}' for d in differences],
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>Difference: %{y:+.2f}<extra></extra>'
        ), row=2, col=2)
        
        # 5. Heatmap Analysis
        if selected_quarter == 'all':
            all_months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        else:
            all_months = q_months[selected_quarter]
            
        year1_monthly = [df[df['Year'] == year1][month].values[0] if len(df[df['Year'] == year1]) > 0 else 0 for month in all_months]
        year2_monthly = [df[df['Year'] == year2][month].values[0] if len(df[df['Year'] == year2]) > 0 else 0 for month in all_months]
        
        heatmap_data = [year1_monthly, year2_monthly]
        fig.add_trace(go.Heatmap(
            z=heatmap_data,
            x=all_months,
            y=[f'{year1}', f'{year2}'],
            colorscale='RdYlBu_r',
            showscale=True,
            hovertemplate='<b>%{y} %{x}</b><br>Value: %{z:.2f}<extra></extra>'
        ), row=3, col=1)
        
        # 6. Box Plot Distribution
        fig.add_trace(go.Box(
            y=year1_data, name=f'{year1}',
            marker=dict(color='#ff6b6b'),
            boxpoints='all',
            jitter=0.3,
            pointpos=-1.8
        ), row=3, col=2)
        
        fig.add_trace(go.Box(
            y=year2_data, name=f'{year2}',
            marker=dict(color='#4ecdc4'),
            boxpoints='all',
            jitter=0.3,
            pointpos=1.8
        ), row=3, col=2)
        
        fig.update_layout(
            height=1400,
            title=dict(
                text=title_text,
                font=dict(size=28, color='#2d3748', family='Inter', weight=700),
                x=0.5, xanchor='center'
            ),
            showlegend=True,
            legend=dict(x=0.85, y=0.95, bgcolor='rgba(255,255,255,0.9)', borderwidth=1),
            plot_bgcolor='rgba(248, 250, 252, 0.5)',
            paper_bgcolor='white',
            font=dict(family='Inter', size=12, color='#2d3748')
        )
    
    graph_html = fig.to_html(full_html=False)
    return render_template('index.html', graph_html=graph_html, selected=view_type, years=years, months=months)

if __name__ == '__main__':
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    app.run(debug=True, port=5001)
