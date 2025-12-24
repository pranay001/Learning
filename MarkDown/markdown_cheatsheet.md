
# Markdown Cheat Sheet and Learning Guide

Markdown is a lightweight markup language for creating formatted text using a plain-text editor. Below is a guide to help you master Markdown syntax.

---

## **Basic Syntax**

### **1. Headers**
Create headers using `#` symbols. The number of `#` determines the header level.

```markdown
# H1 - Largest Header
## H2 - Second Largest
### H3
#### H4
##### H5
###### H6 - Smallest Header
```

**Example Output:**

# H1 - Largest Header  
## H2 - Second Largest  
### H3  
#### H4  
##### H5  
###### H6 - Smallest Header  

---

### **2. Emphasis**
Add emphasis with `*` or `_`.

- **Italic:** `*italic*` or `_italic_` → *italic*
- **Bold:** `**bold**` or `__bold__` → **bold**
- **Bold and Italic:** `***bold and italic***` → ***bold and italic***

---

### **3. Lists**

#### **Unordered List**
Use `-`, `+`, or `*` for bullet points.

```markdown
- Item 1
- Item 2
  - Subitem 2.1
  - Subitem 2.2
```

**Output:**
- Item 1
- Item 2
  - Subitem 2.1
  - Subitem 2.2

#### **Ordered List**
Use numbers followed by a period.

```markdown
1. First
2. Second
3. Third
```

**Output:**
1. First
2. Second
3. Third

---

### **4. Links and Images**

#### **Links**
```markdown
[Link Text](https://example.com)
```
**Example:** [Google](https://google.com)

#### **Images**
```markdown
![Alt Text](https://example.com/image.png)
```
**Example:**  
![Markdown Logo](https://markdown-here.com/img/icon256.png)

---

### **5. Code**

#### **Inline Code**
Wrap code in backticks `` ` ``.
```markdown
`inline code`
```
**Output:** `inline code`

#### **Code Block**
Use triple backticks or indent with 4 spaces.

```markdown
```
code block
```
```

**Output:**
```
code block
```

---

### **6. Blockquotes**
Use `>` to create blockquotes.

```markdown
> This is a blockquote.
> It can span multiple lines.
```

**Output:**
> This is a blockquote.  
> It can span multiple lines.

---

### **7. Tables**
Create tables using pipes `|` and hyphens `-`.

```markdown
| Column 1 | Column 2 | Column 3 |
|----------|----------|----------|
| Data 1   | Data 2   | Data 3   |
| Data 4   | Data 5   | Data 6   |
```

**Output:**

| Column 1 | Column 2 | Column 3 |
|----------|----------|----------|
| Data 1   | Data 2   | Data 3   |
| Data 4   | Data 5   | Data 6   |

---

### **8. Horizontal Line**
Use three dashes `---`, asterisks `***`, or underscores `___` for a horizontal line.

```markdown
---
```

**Output:**
---

---

## **Advanced Syntax**

### **1. Task Lists**
Create task lists with `- [ ]` for incomplete and `- [x]` for complete tasks.

```markdown
- [ ] Task 1
- [x] Task 2 (done)
```

**Output:**
- [ ] Task 1
- [x] Task 2 (done)

---

### **2. Strikethrough**
Use `~~` to strike through text.

```markdown
~~Strikethrough~~
```

**Output:** ~~Strikethrough~~

---

### **3. Escaping Characters**
Use a backslash `\` to escape special characters.

```markdown
\*This text is not italicized.*
```

**Output:** \*This text is not italicized.*

---

### **4. Footnotes**
Add footnotes with `[^1]`.

```markdown
Here is a footnote reference.[^1]

[^1]: This is the footnote text.
```

**Output:**
Here is a footnote reference.[^1]

[^1]: This is the footnote text.

---

### **5. HTML in Markdown**
You can use raw HTML for custom formatting.

```markdown
<strong>This is bold text</strong>
```

**Output:**  
<strong>This is bold text</strong>

---

## **Learning Tips**

1. Practice creating small Markdown files.
2. Use Markdown preview tools (e.g., VS Code, Typora, or online editors like Dillinger).
3. Explore GitHub ReadMe files to see Markdown in action.

For more details, visit the [Markdown Guide](https://www.markdownguide.org/).

---

Happy Markdowning! 🎉