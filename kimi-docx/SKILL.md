---
name: kimi-docx
description: "Professional Word document creation and editing. Create .docx files using C# OpenXML SDK with professional styling, charts, and complex elements. Supports headers, footers, tables, and tracked changes."
---

# Kimi Docx Skill

**Professional Word document creation with OpenXML SDK**

## Tech Stack

| Task | Tool |
|------|------|
| Create documents | C# + OpenXML SDK |
| Edit documents | Python + lxml |
| Validation | OpenXML validator |

## Quick Start

### C# (Document Creation)
```csharp
using DocumentFormat.OpenXml;
using DocumentFormat.OpenXml.Packaging;
using DocumentFormat.OpenXml.Wordprocessing;

// Create document
using var doc = WordprocessingDocument.Create("output.docx");
var body = doc.AddMainDocumentPart().AddNewPart<Body>();
body.Append(new Paragraph(new Run(new Text("Hello World"))));
doc.Save();
```

### Python (Document Editing)
```python
from lxml import etree

tree = etree.parse("input.docx")
# Modify document...
tree.write("output.docx")
```

## Document Structure

```
Document
├── Body
│   ├── Paragraphs
│   ├── Tables
│   ├── Sections
│   └── etc.
├── Header
├── Footer
├── Styles
└── Settings
```

## Basic Paragraph

```csharp
var para = new Paragraph(
    new ParagraphProperties(
        new Justification { Val = JustificationValues.Center }
    ),
    new Run(
        new RunProperties(
            new Bold(),
            new FontSize { Val = "48" }  // 24pt = 48 half-points
        ),
        new Text("Hello World")
    )
);
body.Append(para);
```

## Text Formatting

| Property | XML | Effect |
|----------|-----|--------|
| Bold | `<w:b/>` | **Bold** |
| Italic | `<w:i/>` | *Italic* |
| Underline | `<w:u w:val="single"/>` | Underline |
| Color | `<w:color w:val="FF0000"/>` | Red text |
| Size | `<w:sz w:val="24"/>` | 12pt |

```csharp
var run = new Run(
    new RunProperties(
        new Bold(),
        new Italic(),
        new Color { Val = "0066CC" },
        new FontSize { Val = "28" }
    ),
    new Text("Styled Text")
);
```

## Tables

### Basic Table
```csharp
var table = new Table();

// Table properties (required!)
table.Append(new TableProperties(
    new TableWidth { Width = "5000", Type = TableWidthUnitValues.Dxa },
    new TableBorders(
        new TopBorder { Val = BorderValues.Single, Size = 4 },
        new BottomBorder { Val = BorderValues.Single, Size = 4 },
        new LeftBorder { Val = BorderValues.Single, Size = 4 },
        new RightBorder { Val = BorderValues.Single, Size = 4 }
    )
));

// Table grid (required!)
table.Append(new TableGrid(
    new GridColumn { Width = "2500" },
    new GridColumn { Width = "2500" }
));

// Header row
var headerRow = new TableRow(
    new TableCell(
        new TableCellProperties(new TableCellWidth { Width = "2500" }),
        new Paragraph(new Run(new Bold(), new Text("Column 1")))
    ),
    new TableCell(
        new TableCellProperties(new TableCellWidth { Width = "2500" }),
        new Paragraph(new Run(new Bold(), new Text("Column 2")))
    )
);
table.Append(headerRow);

// Data row
var dataRow = new TableRow(
    new TableCell(
        new Paragraph(new Text("Data 1"))
    ),
    new TableCell(
        new Paragraph(new Text("Data 2"))
    )
);
table.Append(dataRow);

body.Append(table);
```

### Three-Line Table (Academic Style)
```csharp
// Header with bottom border
var headerRow = new TableRow(
    new TableRowProperties(new TableHeader()),
    CreateCell("Header 1", isHeader: true),
    CreateCell("Header 2", isHeader: true)
);

// Data rows with subtle borders
var dataRow = new TableRow(
    CreateCell("Data 1"),
    CreateCell("Data 2")
);

TableCell CreateCell(string text, bool isHeader = false) {
    return new TableCell(
        new TableCellProperties(
            new TableCellWidth { Width = "2500", Type = TableWidthUnitValues.Dxa },
            new TableBorders(
                new BottomBorder { Val = BorderValues.Single, Size = isHeader ? 8 : 4 }
            )
        ),
        new Paragraph(new Run(
            isHeader ? new Bold() : null,
            new Text(text)
        ))
    );
}
```

## Headers & Footers

### Header with Title
```csharp
var headerPart = mainPart.AddNewPart<HeaderPart>();
headerPart.Header = new Header(
    new Paragraph(
        new ParagraphProperties(
            new Justification { Val = JustificationValues.Right }
        ),
        new Run(new Text("Document Title"))
    )
);
var headerId = mainPart.GetIdOfPart(headerPart);
```

### Footer with Page Numbers
```csharp
var footerPart = mainPart.AddNewPart<FooterPart>();
footerPart.Footer = new Footer(
    new Paragraph(
        new ParagraphProperties(
            new Justification { Val = JustificationValues.Center }
        ),
        new Run(new FieldChar { FieldCharType = FieldCharValues.Begin }),
        new Run(new FieldCode(" PAGE ")),
        new Run(new FieldChar { FieldCharType = FieldCharValues.Separate }),
        new Run(new Text("1")),
        new Run(new FieldChar { FieldCharType = FieldCharValues.End })
    )
);
var footerId = mainPart.GetIdOfPart(footerPart);
```

### Link Header/Footer to Section
```csharp
new SectionProperties(
    new HeaderReference { Type = HeaderFooterValues.Default, Id = headerId },
    new FooterReference { Type = HeaderFooterValues.Default, Id = footerId },
    new PageSize { Width = 11906, Height = 16838 },  // A4
    new PageMargin { Top = 1440, Right = 1440, Bottom = 1440, Left = 1440 }
);
```

## Charts

### Pie Chart
```csharp
var chartPart = mainPart.AddChartPart();
chartPart.ChartSpace = new ChartSpace(
    new Chart(
        new Title(ApplyStyleToText(new Text("Sales Distribution"))),
        new PlotArea(
            new PieChartSeries(
                new DataPoint(
                    new NumericValue(30)
                ),
                new DataPoint(
                    new NumericValue(50)
                ),
                new DataPoint(
                    new NumericValue(20)
                )
            )
        )
    )
);
```

## Section Breaks

```csharp
// Continuous section break
new Paragraph(
    new ParagraphProperties(
        new SectionProperties(
            new SectionType { Val = SectionMarkValues.Continuous }
        )
    )
);

// Next page section break
new Paragraph(
    new ParagraphProperties(
        new SectionProperties(
            new SectionType { Val = SectionMarkValues.NextPage }
        )
    )
);
```

## Hyperlinks

```csharp
var relId = mainPart.AddHyperlinkRelationship(
    new Uri("https://example.com"),
    true
).Id;

var hyperlink = new Hyperlink(
    new Run(
        new RunProperties(
            new Color { Val = "0563C1" },
            new Underline { Val = UnderlineValues.Single }
        ),
        new Text("Click here")
    )
) { Id = relId };

body.Append(hyperlink);
```

## Track Changes (Revision Tracking)

```csharp
// Insertion
new InsertedRun(
    new Run(new Text("New text")),
    new InsertedRunProperties(),
    "author",
    DateTime.Now
)

// Deletion
new DeletedRun(
    new Run(new DeletedText("Deleted text")),
    "author",
    DateTime.Now
)
```

## Comments

```csharp
var commentPart = mainPart.AddNewPart<CommentPart>();
commentPart.Comments = new Comments(
    new Comment(
        new Paragraph(new Run(new Text("Comment text"))),
        new ParagraphProperties(
            new ParagraphStyleId { Val = "CommentText" }
        )
    ) { Id = "1", Author = "Author", Date = DateTime.Now }
);
var commentId = mainPart.GetIdOfPart(commentPart);

var paragraphWithComment = new Paragraph(
    new ParagraphProperties(
        new CommentRangeStart { Id = "1" }
    ),
    new Run(new Text("Commented text")),
    new ParagraphProperties(
        new CommentRangeEnd { Id = "1" },
        new CommentReference { Id = "1" }
    )
);
```

## Math Formulas (OMML)

### Basic Fraction
```csharp
new Paragraph(
    new Run(
        new RunProperties(new BalanceSingleByteDoubleByteWidth()),
        new OfficeMath(
            new MathFraction(
                new MathematicalText("a"),
                new MathematicalText("b")
            )
        )
    )
)
```

## Page Elements

### Page Break
```csharp
new Paragraph(
    new Run(
        new Break { Type = BreakValues.Page }
    )
)
```

### Line Spacing
```csharp
new ParagraphProperties(
    new SpacingBetweenLines { After = "200", Line = "276", LineRule = LineSpacingRuleValues.Auto }
)
```

### Keep Lines Together
```csharp
new ParagraphProperties(
    new KeepNext(),
    new KeepLines()
)
```

## Best Practices

1. **Always define styles** - Use `StyleValues` for consistent formatting
2. **Set document margins** - A4 default: 1440 twips (1 inch)
3. **Embed fonts** - For CJK content, use `w:eastAsia` font
4. **Validate output** - Use OpenXML validator before delivery
5. **Test on multiple Office versions** - Especially for complex elements

## Validation Checklist

- [ ] Document opens in Microsoft Word
- [ ] No XML element ordering errors
- [ ] All images embedded (not linked)
- [ ] Fonts available on target system
- [ ] Page numbers working
- [ ] Table of contents refreshes correctly
- [ ] No broken hyperlinks
