# CSV - Reading and Writing CSV Files

**Official Documentation**: https://docs.python.org/3/library/csv.html

Read and write CSV files using Python's built-in `csv` module or `pandas` in NOVA workflows.

---

## Basic Reading with csv module

Read CSV file from bytes or string:

```python
import csv
import io

# From string content
csv_content = context['csv_data']  # String with CSV content
reader = csv.DictReader(io.StringIO(csv_content))

rows = []
for row in reader:
    rows.append(row)
    # row is a dict: {'column1': 'value1', 'column2': 'value2'}

print(f"Read {len(rows)} rows")
```

---

## Reading CSV from Base64

When CSV arrives as base64-encoded attachment:

```python
import csv
import io
import base64

# Decode from base64
csv_bytes = base64.b64decode(context['attachment_data_b64'])
csv_string = csv_bytes.decode('utf-8')  # or 'latin-1' for some files

# Parse CSV
reader = csv.DictReader(io.StringIO(csv_string))
rows = list(reader)

# Access data
for row in rows:
    print(row)  # {'Name': 'John', 'Amount': '100', ...}
```

---

## Reading with pandas (Recommended)

Pandas is more powerful for data manipulation:

```python
import pandas as pd
import io
import base64

# From base64
csv_bytes = base64.b64decode(context['attachment_data_b64'])
df = pd.read_csv(io.BytesIO(csv_bytes))

# From string
df = pd.read_csv(io.StringIO(context['csv_data']))

# Access data
rows = df.to_dict('records')  # List of dicts
# [{'Name': 'John', 'Amount': 100}, {'Name': 'Jane', 'Amount': 200}]

# Column names
columns = df.columns.tolist()  # ['Name', 'Amount', ...]

# Basic stats
total = df['Amount'].sum()
average = df['Amount'].mean()
```

---

## Filtering and Transforming Data

```python
import pandas as pd
import io
import base64

csv_bytes = base64.b64decode(context['attachment_data_b64'])
df = pd.read_csv(io.BytesIO(csv_bytes))

# Filter rows
high_value = df[df['Amount'] > 1000]

# Select columns
subset = df[['Name', 'Amount']]

# Add calculated column
df['Tax'] = df['Amount'] * 0.21

# Group by
by_category = df.groupby('Category')['Amount'].sum()

# Sort
sorted_df = df.sort_values('Amount', ascending=False)

# Convert back to list of dicts
result = df.to_dict('records')
```

---

## Writing CSV

Create CSV output:

```python
import csv
import io

# Data to write
data = [
    {'Name': 'John', 'Amount': 100, 'Date': '2025-01-15'},
    {'Name': 'Jane', 'Amount': 200, 'Date': '2025-01-16'},
]

# Write to string
output = io.StringIO()
writer = csv.DictWriter(output, fieldnames=['Name', 'Amount', 'Date'])
writer.writeheader()
writer.writerows(data)

csv_output = output.getvalue()
```

---

## Writing with pandas

```python
import pandas as pd
import io
import base64

# Create DataFrame
df = pd.DataFrame([
    {'Name': 'John', 'Amount': 100},
    {'Name': 'Jane', 'Amount': 200},
])

# To CSV string
csv_string = df.to_csv(index=False)

# To base64 (for storing in context)
csv_bytes = csv_string.encode('utf-8')
csv_b64 = base64.b64encode(csv_bytes).decode('utf-8')
```

---

## Handling Different Delimiters

CSV files may use different separators:

```python
import pandas as pd
import io

# Semicolon-separated (common in Europe)
df = pd.read_csv(io.StringIO(data), sep=';')

# Tab-separated
df = pd.read_csv(io.StringIO(data), sep='\t')

# Auto-detect delimiter
import csv
dialect = csv.Sniffer().sniff(data[:1024])
df = pd.read_csv(io.StringIO(data), sep=dialect.delimiter)
```

---

## Handling Encodings

```python
import pandas as pd
import io
import base64

csv_bytes = base64.b64decode(context['attachment_data_b64'])

# Try UTF-8 first, fallback to latin-1
try:
    df = pd.read_csv(io.BytesIO(csv_bytes), encoding='utf-8')
except UnicodeDecodeError:
    df = pd.read_csv(io.BytesIO(csv_bytes), encoding='latin-1')
```

---

## Complete Example: Process CSV Attachment

```python
import pandas as pd
import io
import base64
import json

try:
    # Get CSV data from context
    csv_b64 = context.get('attachment_data_b64')
    filename = context.get('attachment_filename', 'data.csv')

    # Decode from base64
    csv_bytes = base64.b64decode(csv_b64)

    # Try to read with pandas
    try:
        df = pd.read_csv(io.BytesIO(csv_bytes), encoding='utf-8')
    except UnicodeDecodeError:
        df = pd.read_csv(io.BytesIO(csv_bytes), encoding='latin-1')

    # Extract data
    rows = df.to_dict('records')
    columns = df.columns.tolist()
    row_count = len(df)

    # Return results
    print(json.dumps({
        "status": "success",
        "context_updates": {
            "extracted_data": rows,
            "column_names": columns,
            "row_count": row_count,
            "source_file": filename
        },
        "message": f"Extracted {row_count} rows from CSV"
    }))

except Exception as e:
    print(json.dumps({
        "status": "error",
        "context_updates": {},
        "message": f"CSV processing error: {str(e)}"
    }))
```

---

## Key Points

- **Use pandas for complex operations**: Filtering, grouping, calculations
- **Use csv module for simple reading**: Less memory, faster for basic needs
- **Handle encodings**: Try UTF-8 first, fallback to latin-1
- **Different delimiters**: European CSVs often use semicolons
- **Base64 for storage**: Store CSV bytes as base64 in NOVA context
- **to_dict('records')**: Convert DataFrame to list of dicts for JSON

---

**Integration**: CSV File Processing (csv + pandas)
**Use with**: Data import, report processing, batch operations
**Official Docs**: https://docs.python.org/3/library/csv.html
