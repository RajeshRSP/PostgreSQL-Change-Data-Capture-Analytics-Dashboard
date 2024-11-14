import pandas as pd
import streamlit as st
import pandas as pd
import plotly.express as px
df = pd.read_parquet("/Users/rajesh_shunmugavel/Downloads/konbert-output-01a9db20.parquet")
df['date']=pd.to_datetime(df['date'], unit='s') 
df['date'] = df['date'].replace('1970-01-01 12:36:19', '2024-11-01')
df['date'] = df['date'].replace('1970-01-01 12:36:20', '2024-11-02')
df['date'] = df['date'].replace('1970-01-01 12:36:21', '2024-11-03')
df['date'] = df['date'].replace('1970-01-01 12:36:22', '2024-11-04')
df  = df.drop(columns = ['column_8','column_9','column_10'])
df['hour'] = df['hour'].astype(int)

dates_mapping = {
    '2024-11-01': '2024-11-05',
    '2024-11-02': '2024-11-06',
    '2024-11-03': '2024-11-07',
    '2024-11-04': '2024-11-08',
}

# Function to shuffle, select, and update the original DataFrame's date
def update_dates_in_df(df, original_date, new_date, rows_to_select):
    # Filter the DataFrame for the original date
    subset = df[df['date'] == original_date]
    
    # Randomly shuffle the rows and select the desired number
    subset_shuffled = subset.sample(n=rows_to_select, random_state=42)
    
    # Update the 'date' in the original DataFrame to the new date for these rows
    df.loc[subset_shuffled.index, 'date'] = new_date

# Process each date and update the original DataFrame
for original_date, new_date in dates_mapping.items():
    update_dates_in_df(df, original_date, new_date, 3084)

def adjust_sums(row):
    if 1 <= row['hour'] <= 8:
        # Reduce all sums by 50%
        row['insert_sum'] *= 0.5
        row['update_sum'] *= 0.5
        row['delete_sum'] *= 0.5
        row['total'] *= 0.5
    elif 8 < row['hour'] <= 11:
        # Reduce all sums by 20%
        row['insert_sum'] *= 0.8
        row['update_sum'] *= 0.8
        row['delete_sum'] *= 0.8
        row['total'] *= 0.8
    elif 12 <= row['hour'] <= 16:
        # Increase all sums by 20%
        row['insert_sum'] *= 1.2
        row['update_sum'] *= 1.2
        row['delete_sum'] *= 1.2
        row['total'] *= 1.2
    elif 16 < row['hour'] <= 24:
        # Reduce all sums by 50%
        row['insert_sum'] *= 0.5
        row['update_sum'] *= 0.5
        row['delete_sum'] *= 0.5
        row['total'] *= 0.5
    
    return row

# Apply the function to each row of the DataFrame
df = df.apply(adjust_sums, axis=1)
# Streamlit setup
st.title('DB Operations Summary')

# User input for start and end date
col1, col2 = st.columns(2)

# Place the start date input in the first column
start_date = col1.text_input('Enter start date (YYYY-MM-DD)', '')

# Place the end date input in the second column
end_date = col2.text_input('Enter end date (YYYY-MM-DD)', '')

#get start,end date
# start_date = '2024-11-01'
# end_date = '2024-11-01'

start_date = pd.to_datetime(start_date)
end_date = pd.to_datetime(end_date)

# Get unique table names
table_names = df['table_name'].unique()

# Add multiselect for selecting table names
selected_tables = st.multiselect("Select tables (Leave it blank to select all)", table_names)

# Filter data based on selected table names
df = df[df['table_name'].isin(selected_tables)]

filtered_df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]

#get table name

# filtered_df= date_filterred_df[date_filterred_df['table_name'] == 'lit_docs_claim_term_pat_claims']

#plot stacked bar
# filtered_df['insert_sum'].sum()
# filtered_df['update_sum'].sum()
# filtered_df['delete_sum'].sum()
# filtered_df['total'].sum()



st.title("Stacked Bar Chart of Operations Over Time")

# Melt the operations DataFrame to long format for plotting
df_operations_long = filtered_df.melt(id_vars='date', value_vars=['insert_sum', 'update_sum', 'delete_sum'],
                                         var_name='operation', value_name='count')

# Create the first stacked bar chart for operations
fig_operations = px.bar(df_operations_long,
                        x='date',
                        y='count',
                        color='operation',
                        title="Operation Counts per Date",
                        labels={'count': 'Count of Operations', 'date': 'Date'},
                        height=400)

# Adjust the bar width (thin bars)
fig_operations.update_layout(bargap=0.1)

# Display the first chart in Streamlit
st.plotly_chart(fig_operations)



##second chart

# Streamlit Title for the second chart
st.subheader("Hourly Distribution of Operations")


df_hourly = filtered_df.groupby('hour', as_index=False)['total'].sum()
# Create the second bar chart for hourly distribution
fig_hourly = px.bar(df_hourly,
                    x='hour',
                    y='total',
                    # color='hour',
                    title="Total Operations per Hour of the Day",
                    labels={'total': 'Total Operations', 'hour': 'Hour of the Day'},
                    height=400)

# Display the second chart in Streamlit
st.plotly_chart(fig_hourly)



df_tables = filtered_df[['table_name','total']]
df_top_tables = df_tables.sort_values(by='total', ascending=False).head(10)

# Streamlit app title
st.title("Top 10 Tables with Most Operations")

# Create a horizontal bar chart for top 10 tables without color differentiation
fig_tables = px.bar(df_top_tables,
                    x='total',
                    y='table_name',
                    orientation='h',
                    title="Top 10 Tables with Most Operations",
                    labels={'total': 'Total Operations', 'table_name': 'Table Name'},
                    height=400)

# Customize the layout for better appearance (optional)
fig_tables.update_layout(
    xaxis_title="Total Operations",
    yaxis_title="Table Name",
    xaxis=dict(tickformat=",.0f"),  # Format the x-axis to display numbers cleanly
    showlegend=False  # Hide the legend
)

# Display the bar chart in Streamlit
st.plotly_chart(fig_tables)

