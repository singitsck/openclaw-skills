---
name: kimi-pdf
description: "Professional PDF solution with HTML, LaTeX, and Python processing routes. Create PDFs using HTML+Paged.js, process existing PDFs, or compile LaTeX. Supports math formulas, diagrams, and academic papers."
---

# Kimi PDF Skill

**Multi-route PDF processing: Create, Process, and Compile**

## Route Selection

| Route | Use Case | Tools |
|-------|----------|-------|
| **HTML** (default) | Reports, papers, documents | Playwright + Paged.js |
| **LaTeX** | Academic papers, theses | Tectonic compiler |
| **Process** | Extract, merge, split, fill forms | Python (pikepdf, pdfplumber) |

## Quick Start

```bash
# Check environment
which chromium playwright python3

# HTML to PDF (default route)
pandoc input.html -o output.pdf

# Or use CLI if available
pdf-tool html input.html output.pdf
```

## Route 1: HTML → PDF (Default)

### Setup
```bash
# Install Playwright
npm install -g playwright
npx playwright install chromium
```

### HTML Template
```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Document</title>
  <style>
    @page { size: A4; margin: 2cm; }
    body { font-family: system-ui; }
    h1 { font-size: 24pt; }
  </style>
</head>
<body>
  <h1>Title</h1>
  <p>Content here...</p>
</body>
</html>
```

### Convert
```bash
# Using Puppeteer
node << 'EOF'
const puppeteer = require('puppeteer');
(async () => {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();
  await page.goto('file://' + process.cwd() + '/input.html');
  await page.pdf({ path: 'output.pdf', format: 'A4' });
  await browser.close();
})();
EOF
```

## Route 2: LaTeX → PDF

### Setup
```bash
# Install Tectonic (LaTeX compiler)
# macOS
brew install tectonic
# Linux
curl -L https://get.tectonic.gallery | bash
```

### LaTeX Template
```latex
\documentclass[12pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage{amsmath}
\usepackage{graphicx}

\title{Document Title}
\author{Author Name}

\begin{document}
\maketitle

\section{Introduction}
Your content here.

\end{document}
```

### Compile
```bash
tectonic document.tex --output-dir .
```

## Route 3: Process Existing PDF

### Python Libraries
```bash
pip install pikepdf pdfplumber pypdf2 reportlab pytesseract
```

### Extract Text
```python
import pdfplumber

with pdfplumber.open("input.pdf") as pdf:
    for page in pdf.pages:
        text = page.extract_text()
        print(text)
```

### Extract Tables
```python
import pdfplumber

with pdfplumber.open("input.pdf") as pdf:
    for page in pdf.pages:
        tables = page.extract_tables()
        for table in tables:
            print(table)
```

### Merge PDFs
```python
from PyPDF2 import Merger

merger = Merger()
merger.append("file1.pdf")
merger.append("file2.pdf")
merger.write("merged.pdf")
merger.close()
```

### Split PDF
```python
from PyPDF2 import PdfReader, PdfWriter

reader = PdfReader("input.pdf")
for i, page in enumerate(reader.pages):
    writer = PdfWriter()
    writer.add_page(page)
    with open(f"page_{i}.pdf", "wb") as f:
        writer.write(f)
```

### Rotate Pages
```python
from PyPDF2 import PdfReader, PdfWriter

reader = PdfReader("input.pdf")
writer = PdfWriter()
for page in reader.pages:
    page.rotate(90)  # Rotate 90 degrees
    writer.add_page(page)
with open("rotated.pdf", "wb") as f:
    writer.write(f)
```

### Fill Form Fields
```python
from PyPDF2 import PdfReader, PdfWriter
from PyPDF2.fields import flatten_fields

reader = PdfReader("form.pdf")
writer = PdfWriter()
writer.add_page(reader.pages[0])

writer.update_page_form_field_values(
    writer.pages[0],
    {"name": "John Doe", "email": "john@example.com"}
)

with open("filled.pdf", "wb") as f:
    writer.write(f)
```

## Advanced Features

### Math Formulas (KaTeX)
```html
<head>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css">
  <script src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>
</head>
<body>
  <p>Inline: $E = mc^2$</p>
  <p>Block:</p>
  <div data-formula="\int_0^\infty e^{-x^2} dx = \frac{\sqrt{\pi}}{2}"></div>
</body>
```

### Mermaid Diagrams
```html
<script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
<pre class="mermaid">
graph TD
  A[Start] --> B{Decision}
  B -->|Yes| C[Action]
  B -->|No| D[End]
</pre>
```

### Charts with Chart.js
```html
<canvas id="myChart" width="400" height="200"></canvas>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script>
  new Chart(document.getElementById('myChart'), {
    type: 'bar',
    data: { labels: ['A', 'B', 'C'], datasets: [{ data: [10, 20, 30] }] }
  });
</script>
```

## OCR (Extract from Scanned PDF)
```python
import pytesseract
from pdf2image import convert_from_path

images = convert_from_path("scanned.pdf")
text = ""
for image in images:
    text += pytesseract.image_to_string(image)
print(text)
```

## Cover Page Design

### Minimal (Academic)
```html
<div class="cover-minimal">
  <h1>Paper Title</h1>
  <p class="author">Author Name</p>
  <p class="date">January 2026</p>
</div>
```

### Professional
```html
<div class="cover-professional">
  <div class="company-logo">Company</div>
  <h1>Report Title</h1>
  <p class="subtitle">Subtitle</p>
  <div class="meta">
    <p>Date: January 2026</p>
    <p>Author: Name</p>
  </div>
</div>
```

## Best Practices

1. **File Size** - Optimize images before embedding
2. **Fonts** - Embed fonts for consistent rendering
3. **Colors** - Use CMYK for print, RGB for screen
4. **Links** - Add hyperlinks with `https://`
5. **Metadata** - Set title, author, keywords

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Chinese text not rendering | Use Noto Sans CJK fonts |
| Images too large | Compress with `pngquant` |
| Memory error | Process pages in batches |
| Form not filling | Check field names with `pdf-tool inspect` |
