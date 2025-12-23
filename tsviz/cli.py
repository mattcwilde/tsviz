"""CLI for time series visualization."""
import sys
from pathlib import Path
import click
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

PALETTE_NAMED = {
    "off_white": "#FDFDFD",
    "light_sage_gray": "#DBE0D7",
    "warm_tan": "#BBA178",
    "muted_sage_green": "#8C9785",
    "cool_blue_gray": "#BACCCC",
    "slate_blue_gray": "#5A6876",
    "charcoal": "#201C1A",
}

PALETTE_COLORS = [
    PALETTE_NAMED["slate_blue_gray"],
    PALETTE_NAMED["warm_tan"],
    PALETTE_NAMED["cool_blue_gray"],
    PALETTE_NAMED["muted_sage_green"],
    PALETTE_NAMED["light_sage_gray"],
]


def detect_time_column(df):
    """Detect the time series column in the dataframe."""
    datetime_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
    if datetime_cols:
        return datetime_cols[0]
    
    for col in df.columns:
        try:
            pd.to_datetime(df[col], errors='raise')
            return col
        except (ValueError, TypeError):
            continue
    
    if df.index.name and isinstance(df.index, pd.DatetimeIndex):
        return None
    
    return None


def prepare_data(file_path, columns=None):
    """Load and prepare data from file."""
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    if file_path.suffix.lower() == '.csv':
        df = pd.read_csv(file_path)
    elif file_path.suffix.lower() in ['.xlsx', '.xls']:
        df = pd.read_excel(file_path)
    else:
        raise ValueError(f"Unsupported file format: {file_path.suffix}")
    
    time_col = detect_time_column(df)
    
    # Fallback for headerless single-column CSVs (Xendee curves)
    if time_col is None and file_path.suffix.lower() == '.csv' and len(df.columns) == 1 and not pd.api.types.is_numeric_dtype(df[df.columns[0]]):
        df = pd.read_csv(file_path, header=None, names=['value'])
        time_col = detect_time_column(df)
    
    if time_col is None:
        if isinstance(df.index, pd.DatetimeIndex):
            df = df.reset_index()
            time_col = df.columns[0]
        else:
            # If only one numeric column and no datetime detected, assume Xendee curve (8760 hourly values)
            numeric_cols = [col for col in df.columns if pd.api.types.is_numeric_dtype(df[col])]
            if len(numeric_cols) == 1:
                time_col = 'datetime'
                df[time_col] = pd.date_range('2027-01-01', periods=len(df), freq='H')
            else:
                raise ValueError("No datetime column found in the file")
    
    df[time_col] = pd.to_datetime(df[time_col])
    
    df = df.dropna(axis=1, how='all')
    
    if columns:
        missing_cols = [col for col in columns if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Columns not found: {', '.join(missing_cols)}")
        value_cols = columns
    else:
        value_cols = [col for col in df.columns if col != time_col]
        value_cols = [col for col in value_cols if pd.api.types.is_numeric_dtype(df[col])]
    
    if not value_cols:
        raise ValueError("No numeric columns found to plot")
    
    return df, time_col, value_cols


def create_plot(df, time_col, value_cols):
    """Create interactive plotly plot."""
    fig = go.Figure()
    
    has_year = df[time_col].dt.year.notna().any()
    
    for idx, col in enumerate(value_cols):
        color = PALETTE_COLORS[idx % len(PALETTE_COLORS)]
        
        hover_template = f"<b>{col}</b><br>"
        hover_template += "Date: %{x|%Y-%m-%d %H:%M:%S}<br>"
        
        if has_year:
            df['_day_of_week'] = df[time_col].dt.day_name()
            customdata = df[['_day_of_week']].values
            hover_template += "Day: %{customdata[0]}<br>"
        else:
            customdata = None
        
        hover_template += f"Value: %{{y:,.2f}}<extra></extra>"
        
        fig.add_trace(go.Scatter(
            x=df[time_col],
            y=df[col],
            mode='lines',
            name=col,
            customdata=customdata,
            hovertemplate=hover_template,
            line=dict(color=color, width=2.5)
        ))
    
    fig.update_layout(
        title="Time Series Visualization",
        xaxis_title="Time",
        yaxis_title="Value",
        hovermode='closest',
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor=f"rgba(253, 253, 253, 0.8)",
            bordercolor=PALETTE_NAMED["light_sage_gray"],
            borderwidth=1
        ),
        plot_bgcolor=PALETTE_NAMED["off_white"],
        paper_bgcolor=PALETTE_NAMED["off_white"],
        font=dict(color=PALETTE_NAMED["charcoal"], family="Arial, sans-serif"),
        xaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor=PALETTE_NAMED["light_sage_gray"],
            zeroline=False
        ),
        yaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor=PALETTE_NAMED["light_sage_gray"],
            zeroline=False,
            rangemode="tozero"
        )
    )
    
    return fig


@click.command()
@click.argument('file', type=click.Path(exists=True))
@click.option('-c', '--columns', multiple=True, help='Column names to plot (can be specified multiple times)')
@click.option('-o', '--output', type=click.Path(), help='Save plot to HTML file instead of opening browser')
@click.option('-t', '--title', help='Custom title for the plot')
def main(file, columns, output, title):
    """
    Create interactive time series visualizations from CSV or Excel files.
    
    Examples:
    
        tsviz data.csv
        
        tsviz data.csv -c column1 -c column2
        
        tsviz data.xlsx -o output.html
        
        tsviz data.csv -c temperature -t "Temperature Over Time"
    """
    try:
        df, time_col, value_cols = prepare_data(file, list(columns) if columns else None)
        
        click.echo(f"Time column: {time_col}")
        click.echo(f"Plotting columns: {', '.join(value_cols)}")
        click.echo(f"Data points: {len(df)}")
        
        fig = create_plot(df, time_col, value_cols)
        
        if title:
            fig.update_layout(title=title)
        
        if output:
            fig.write_html(output)
            click.echo(f"Plot saved to: {output}")
        else:
            fig.show()
            click.echo("Plot opened in browser")
        
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
