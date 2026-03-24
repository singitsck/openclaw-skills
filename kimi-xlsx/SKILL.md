---
name: kimi-xlsx
description: "Advanced Excel spreadsheet creation and analysis using Python + openpyxl/pandas. Professional financial modeling with rigorous validation pipeline, PivotTable support, and comprehensive formula error checking. Enhanced with KimiXlsx CLI tools."
---

# Kimi XLSX Skill

**Enhanced Excel creation with professional validation pipeline**

## Tech Stack

- **Runtime**: Python 3
- **Primary Library**: openpyxl (Excel creation, styling, formulas)
- **Data Processing**: pandas (data manipulation, export via openpyxl)
- **CLI Tools**: KimiXlsx (validation, recheck, pivot, chart-verify)

## Quick Start

```bash
# Check environment
python3 -c "import openpyxl, pandas; print('OK')"

# Create Excel file
python3 << 'EOF'
from openpyxl import Workbook

wb = Workbook()
ws = wb.active
ws['A1'] = "Header"
ws['B1'] = 100
ws['C1'] = '=B1*0.1'  # Use formulas!
wb.save('output.xlsx')
EOF
```

## CLI Tools

**KimiXlsx** (if available):
```bash
# Validation commands
kimi-xlsx recheck output.xlsx        # Check formula errors
kimi-xlsx reference-check output.xlsx # Check reference issues
kimi-xlsx validate output.xlsx       # Final OpenXML validation
kimi-xlsx inspect input.xlsx         # Analyze structure
kimi-xlsx chart-verify output.xlsx   # Verify charts
```

## Workflow

### 1. Plan Sheet Structure
Before coding, design:
- What data goes in this sheet
- What formulas are needed
- Cross-sheet references
- Formatting style

### 2. Create & Validate (Per-Sheet Loop)

```
For each sheet:
 1. CREATE → Write data, formulas, styling
 2. SAVE → wb.save()
 3. CHECK → recheck + reference-check
 4. FIX → If errors found, fix and repeat
 5. NEXT → Only proceed after 0 errors
```

### 3. Final Validation
```bash
kimi-xlsx validate output.xlsx  # Exit code 0 = safe to deliver
```

## Formula Guidelines

### ✅ Use Excel Formulas (NOT Python calculations)
```python
# GOOD - Excel formula
ws['C2'] = '=A2+B2'
ws['D2'] = '=SUM(A2:A100)'

# BAD - Pre-calculated static value
ws['C2'] = 150  # Don't do this for calculations
```

### ✅ Color Coding Standard
| Color | Meaning |
|-------|---------|
| Blue | Input values (hardcoded) |
| Black | Formula cells |
| Green | References to other sheets |
| Red | External data references |

### ✅ Financial Values
- Store in smallest unit (15000000 not 1.5M)
- Use format: `"¥#,##0"` or `"$#,##0"`

## Forbidden Functions

These functions are NOT supported in Excel 2019 and earlier:
- FILTER(), UNIQUE(), SORT(), SORTBY()
- XLOOKUP(), XMATCH(), SEQUENCE()
- LET(), LAMBDA(), RANDARRAY()

**Alternative**: Use SUMIF, COUNTIF, INDEX-MATCH, or PivotTable instead.

## PivotTable Creation

When user requests "pivot table" or "summarize by category":

1. Prepare data in a sheet
2. Use PivotTable command (if KimiXlsx available)
3. NEVER manually construct pivot with openpyxl

## Chart Creation

```python
from openpyxl.chart import BarChart, Reference

chart = BarChart()
chart.type = "col"
chart.title = "Sales by Category"
data = Reference(ws, min_col=2, min_row=1, max_row=4)
chart.add_data(data, titles_from_data=True)
ws.add_chart(chart, "E2")
```

## Validation Checklist

Before delivery:
- [ ] No formula errors (#VALUE!, #DIV/0!, #REF!, #N/A)
- [ ] Zero-value cells verified (often indicates reference error)
- [ ] All numbers in numeric format (not text)
- [ ] Currency format with symbol
- [ ] Gridlines hidden (professional look)
- [ ] Headers have proper styling

## External Data Citation

When using external data:
- Add `Source Name` and `Source URL` columns
- Or create a "Sources" sheet
- DO NOT deliver external data without citations
