import pandas as pd
import streamlit as st
import plotly.express as px

# Function to filter the dataframe based on date range and selected tables
def filter_data(df, start_date, end_date, selected_tables):
    # Convert start and end dates to datetime
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    
    # Filter the data by table names and date range
    filtered_df = df[df['table_name'].isin(selected_tables)]
    filtered_df = filtered_df[(filtered_df['date'] >= start_date) & (filtered_df['date'] <= end_date)]
    
    return filtered_df

# Function to plot operation counts per date
def plot_operations_per_date(filtered_df):
    # Melt the operations DataFrame to long format
    df_operations_long = filtered_df.melt(id_vars='date', value_vars=['insert_sum', 'update_sum', 'delete_sum'],
                                         var_name='operation', value_name='count')
    
    # Create the stacked bar chart
    fig_operations = px.bar(df_operations_long,
                            x='date',
                            y='count',
                            color='operation',
                            title="Operation Counts per Date",
                            labels={'count': 'Count of Operations', 'date': 'Date'},
                            height=400)
    
    # Adjust the bar width (thin bars)
    fig_operations.update_layout(bargap=0.1)
    
    # Display the chart
    st.plotly_chart(fig_operations)

# Function to plot total operations per hour
def plot_operations_per_hour(filtered_df):
    # Group by hour and sum the total operations
    df_hourly = filtered_df.groupby('hour', as_index=False)['total'].sum()
    
    # Create the bar chart
    fig_hourly = px.bar(df_hourly,
                        x='hour',
                        y='total',
                        title="Total Operations per Hour of the Day",
                        labels={'total': 'Total Operations', 'hour': 'Hour of the Day'},
                        height=400)
    
    # Display the chart
    st.plotly_chart(fig_hourly)

# Function to plot top 10 tables with most operations
def plot_top_tables(filtered_df):
    # Get top 10 tables with most operations
    df_tables = filtered_df[['table_name', 'total']]
    df_top_tables = df_tables.sort_values(by='total', ascending=False).head(10)
    
    # Create the bar chart
    fig_tables = px.bar(df_top_tables,
                        x='total',
                        y='table_name',
                        orientation='h',
                        title="Top 10 Tables with Most Operations",
                        labels={'total': 'Total Operations', 'table_name': 'Table Name'},
                        height=400)
    
    # Customize the layout
    fig_tables.update_layout(
        xaxis_title="Total Operations",
        yaxis_title="Table Name",
        xaxis=dict(tickformat=",.0f"),
        showlegend=False
    )
    
    # Display the chart
    st.plotly_chart(fig_tables)

# Main function to run the Streamlit app
def main():
    # Load the data
    file_path = <path to parquet file>
    df = pd.read_parquet(file_path)

    # Set up Streamlit UI
    st.title('DB Operations Summary')

    # User input for start and end date
    col1, col2 = st.columns(2)
    start_date = col1.text_input('Enter start date (YYYY-MM-DD)', '')
    end_date = col2.text_input('Enter end date (YYYY-MM-DD)', '')
    
    # Convert to datetime
    try:
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
    except ValueError:
        st.error("Please enter valid start and end dates in the format YYYY-MM-DD.")
        return

    # Get unique table names
    table_names = df['table_name'].unique()
    selected_tables = st.multiselect("Select tables (Leave it blank to select all)", table_names)

    if not selected_tables:
        selected_tables = table_names  # Select all tables if none are selected

    # Filter the data
    filtered_df = filter_data(df, start_date, end_date, selected_tables)

    # Plot the various charts
    plot_operations_per_date(filtered_df)
    plot_operations_per_hour(filtered_df)
    plot_top_tables(filtered_df)

# Run the main function
if __name__ == "__main__":
    main()
