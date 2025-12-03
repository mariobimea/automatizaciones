# XLSX - Reading and Writing Excel Files

**Official Documentation**: https://openpyxl.readthedocs.io/

Read and write Excel files (.xlsx) using `openpyxl` or `pandas` in NOVA workflows.

---

## Basic Reading with openpyxl

Read Excel file from bytes:

```python
import openpyxl
import io
import base64

# Decode from base64
xlsx_bytes = base64.b64decode(context['attachment_data_b64'])

# Load workbook
wb = openpyxl.load_workbook(io.BytesIO(xlsx_bytes))

# Get sheet names
sheet_names = wb.sheetnames  # ['Sheet1', 'Sheet2', ...]

# Get active sheet
sheet = wb.active

# Or get specific sheet
sheet = wb['Sheet1']

# Read all rows
rows = []
for row in sheet.iter_rows(min_row=2, values_only=True):  # Skip header
    rows.append(row)

# Get header
header = [cell.value for cell in sheet[1]]

wb.close()
```

---

## Reading as Dictionary

Convert rows to dictionaries with column names:

```python
import openpyxl
import io
import base64

xlsx_bytes = base64.b64decode(context['attachment_data_b64'])
wb = openpyxl.load_workbook(io.BytesIO(xlsx_bytes))
sheet = wb.active

# Get header from first row
header = [cell.value for cell in sheet[1]]

# Convert rows to dicts
rows = []
for row in sheet.iter_rows(min_row=2, values_only=True):
    row_dict = dict(zip(header, row))
    rows.append(row_dict)

# rows = [{'Name': 'John', 'Amount': 100}, {'Name': 'Jane', 'Amount': 200}]

wb.close()
```

---

## Reading with pandas (Recommended)

Pandas makes Excel reading much simpler:

```python
import pandas as pd
import io
import base64

# Decode from base64
xlsx_bytes = base64.b64decode(context['attachment_data_b64'])

# Read Excel file
df = pd.read_excel(io.BytesIO(xlsx_bytes), engine='openpyxl')

# Convert to list of dicts
rows = df.to_dict('records')

# Column names
columns = df.columns.tolist()

# Number of rows
row_count = len(df)
```

---

## Reading Specific Sheet

```python
import pandas as pd
import io
import base64

xlsx_bytes = base64.b64decode(context['attachment_data_b64'])

# Read specific sheet by name
df = pd.read_excel(io.BytesIO(xlsx_bytes), sheet_name='Invoices', engine='openpyxl')

# Read specific sheet by index (0-based)
df = pd.read_excel(io.BytesIO(xlsx_bytes), sheet_name=0, engine='openpyxl')

# Read all sheets (returns dict of DataFrames)
all_sheets = pd.read_excel(io.BytesIO(xlsx_bytes), sheet_name=None, engine='openpyxl')
# all_sheets = {'Sheet1': df1, 'Sheet2': df2, ...}
```

---

## Getting Sheet Names

```python
import pandas as pd
import io
import base64

xlsx_bytes = base64.b64decode(context['attachment_data_b64'])

# Get sheet names without reading data
xlsx_file = pd.ExcelFile(io.BytesIO(xlsx_bytes), engine='openpyxl')
sheet_names = xlsx_file.sheet_names  # ['Sheet1', 'Sheet2', ...]
xlsx_file.close()
```

---

## Reading Legacy Excel (.xls)

For old Excel format, use xlrd:

```python
import pandas as pd
import io
import base64

xls_bytes = base64.b64decode(context['attachment_data_b64'])

# xlrd is used automatically for .xls files
df = pd.read_excel(io.BytesIO(xls_bytes), engine='xlrd')
```

---

## Writing Excel Files

Create new Excel file:

```python
import openpyxl
import io
import base64

# Create workbook
wb = openpyxl.Workbook()
sheet = wb.active
sheet.title = "Data"

# Write header
sheet.append(['Name', 'Amount', 'Date'])

# Write data rows
data = [
    ['John', 100, '2025-01-15'],
    ['Jane', 200, '2025-01-16'],
]
for row in data:
    sheet.append(row)

# Save to bytes
output = io.BytesIO()
wb.save(output)
xlsx_bytes = output.getvalue()

# Convert to base64 for storage
xlsx_b64 = base64.b64encode(xlsx_bytes).decode('utf-8')

wb.close()
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

# Write to Excel bytes
output = io.BytesIO()
df.to_excel(output, index=False, engine='openpyxl')
xlsx_bytes = output.getvalue()

# Convert to base64
xlsx_b64 = base64.b64encode(xlsx_bytes).decode('utf-8')
```

---

## Multiple Sheets

Write multiple sheets:

```python
import pandas as pd
import io
import base64

df1 = pd.DataFrame([{'Name': 'John', 'Amount': 100}])
df2 = pd.DataFrame([{'Product': 'Widget', 'Price': 50}])

output = io.BytesIO()
with pd.ExcelWriter(output, engine='openpyxl') as writer:
    df1.to_excel(writer, sheet_name='Invoices', index=False)
    df2.to_excel(writer, sheet_name='Products', index=False)

xlsx_bytes = output.getvalue()
xlsx_b64 = base64.b64encode(xlsx_bytes).decode('utf-8')
```

---

## Complete Example: Process Excel Attachment

```python
import pandas as pd
import io
import base64
import json

try:
    # Get Excel data from context
    xlsx_b64 = context.get('attachment_data_b64')
    filename = context.get('attachment_filename', 'data.xlsx')

    # Decode from base64
    xlsx_bytes = base64.b64decode(xlsx_b64)

    # Detect file type and read accordingly
    if filename.lower().endswith('.xls'):
        df = pd.read_excel(io.BytesIO(xlsx_bytes), engine='xlrd')
    else:
        df = pd.read_excel(io.BytesIO(xlsx_bytes), engine='openpyxl')

    # Extract data
    rows = df.to_dict('records')
    columns = df.columns.tolist()
    row_count = len(df)

    # Get sheet names for multi-sheet files
    xlsx_file = pd.ExcelFile(io.BytesIO(xlsx_bytes), engine='openpyxl')
    sheet_names = xlsx_file.sheet_names
    xlsx_file.close()

    # Return results
    print(json.dumps({
        "status": "success",
        "context_updates": {
            "extracted_data": rows,
            "column_names": columns,
            "row_count": row_count,
            "sheet_names": sheet_names,
            "source_file": filename
        },
        "message": f"Extracted {row_count} rows from Excel"
    }))

except Exception as e:
    print(json.dumps({
        "status": "error",
        "context_updates": {},
        "message": f"Excel processing error: {str(e)}"
    }))
```

---

## Handling Data Types

Excel cells can have different types:

```python
import pandas as pd
import io
import base64

xlsx_bytes = base64.b64decode(context['attachment_data_b64'])
df = pd.read_excel(io.BytesIO(xlsx_bytes), engine='openpyxl')

# Convert dates to strings for JSON serialization
for col in df.select_dtypes(include=['datetime64']).columns:
    df[col] = df[col].dt.strftime('%Y-%m-%d')

# Handle NaN values (replace with None for JSON)
df = df.where(pd.notnull(df), None)

rows = df.to_dict('records')
```

---

## Key Points

- **Use pandas for reading**: Simpler API than openpyxl
- **engine='openpyxl'**: Required for .xlsx files
- **engine='xlrd'**: Required for legacy .xls files
- **to_dict('records')**: Convert DataFrame to list of dicts
- **Handle dates**: Convert datetime to string for JSON
- **Handle NaN**: Replace with None for JSON serialization
- **Multiple sheets**: Use sheet_name parameter or read all with sheet_name=None
- **Base64 for storage**: Store Excel bytes as base64 in NOVA context

---

**Integration**: Excel File Processing (openpyxl + pandas)
**Use with**: Data import, report generation, spreadsheet automation
**Official Docs**: https://openpyxl.readthedocs.io/
