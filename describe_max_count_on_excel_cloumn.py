
import pandas as pd

def data_read(url: str):
    # Read Excel file
    data_df = pd.read_excel(url, header=None)

    # Assign custom headers
    data_df.columns = ['Description', 'Priority', 'ShortDescription', 'ConfigurationItem',
                       'ElapsedTime', 'ContactNotes', 'ResolutionCode', 'ClosureCode']

    # Copy DataFrame
    data_df_copy = data_df.copy()

    # Extract columns
    description = data_df_copy['Description']
    resolutioncode = data_df_copy['ResolutionCode']

    return description, resolutioncode


# Call function
description, resolutioncode = data_read('/content/colab_data_llm.xlsx')

# Show statistics for ResolutionCode
print("ResolutionCode Statistics:")
print(resolutioncode.describe())

# Show most frequent value and its count
top_value = resolutioncode.value_counts().idxmax()
top_count = resolutioncode.value_counts().max()

print(f"\nMost frequent ResolutionCode: {top_value} (Count: {top_count})")

