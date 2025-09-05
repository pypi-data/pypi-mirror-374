# Output Format Instructions

## Review Output Structure

Your review must be structured as a valid JSON object with the following format:

```json
{
  "summary": "Brief overview of the overall code quality and key findings",
  "severity_counts": {
    "critical": 0,
    "major": 0,
    "minor": 0,
    "info": 0
  },
  "changes": [
    {
      "file_path": "path/to/file.py",
      "start_line": 15,
      "end_line": 23,
      "severity": "major",
      "category": "security|performance|maintainability|architecture|style",
      "title": "Brief, descriptive title for the issue",
      "description": "Detailed explanation of the problem",
      "suggestion": "Specific recommendation for how to fix it",
      "code_snippet": "The problematic code snippet",
      "suggested_code": "The improved code suggestion",
      "rationale": "Why this change improves the code"
    }
  ],
  "positives": [
    "List of good practices and positive aspects found in the code"
  ],
  "recommendations": [
    "High-level suggestions for future improvements"
  ]
}
```

## Field Requirements

### Summary
- **Required**: Yes
- **Format**: String, 2-3 sentences
- **Content**: Overall assessment of code quality, main concerns, and positive aspects

### Severity Counts
- **Required**: Yes
- **Format**: Object with numeric counts
- **Levels**:
  - `critical`: Security issues, data corruption risks, system crashes
  - `major`: Logic errors, performance issues, maintainability problems
  - `minor`: Style issues, documentation gaps, minor inefficiencies
  - `info`: Suggestions for improvement, best practices

### Changes Array
- **Required**: Yes (can be empty array)
- **Each Change Object**:
  - `file_path`: Full path to the file
  - `start_line`: Starting line number of the issue
  - `end_line`: Ending line number of the issue
  - `severity`: One of: "critical", "major", "minor", "info"
  - `category`: One of: "security", "performance", "maintainability", "architecture", "style"
  - `title`: Concise, descriptive title (max 80 characters)
  - `description`: Clear explanation of what's wrong
  - `suggestion`: Actionable fix recommendation
  - `code_snippet`: The actual problematic code (escaped for JSON)
  - `suggested_code`: The improved code (escaped for JSON)
  - `rationale`: Why this change is beneficial

### Positives Array
- **Required**: No
- **Format**: Array of strings
- **Content**: Positive aspects, good practices, well-written code sections

### Recommendations Array
- **Required**: No
- **Format**: Array of strings
- **Content**: High-level suggestions for future development

## Output Guidelines

### Code Snippets
- Include the actual problematic code in `code_snippet`
- Provide improved code in `suggested_code`
- Use proper indentation and formatting
- Escape special characters for JSON compatibility

### Severity Assignment
- **Critical**: Issues that could cause security breaches, data loss, or system failures
- **Major**: Logic errors, performance bottlenecks, maintainability issues
- **Minor**: Style violations, documentation issues, small inefficiencies
- **Info**: Suggestions for improvement, best practice recommendations

### Categories
- **Security**: Authentication, authorization, input validation, encryption
- **Performance**: Algorithm efficiency, memory usage, database queries
- **Maintainability**: Code structure, naming, complexity, documentation
- **Architecture**: Design patterns, component coupling, scalability
- **Style**: Code formatting, naming conventions, language idioms

### Quality Standards
- Every change must have a clear, actionable suggestion
- Include specific line numbers for all issues
- Provide rationale for why changes are needed
- Balance criticism with recognition of good practices
- Prioritize the most important issues

## Example Output

```json
{
  "summary": "The code introduces a new authentication feature with good error handling but has a potential security vulnerability in input validation.",
  "severity_counts": {
    "critical": 1,
    "major": 2,
    "minor": 1,
    "info": 3
  },
  "changes": [
    {
      "file_path": "auth/login.py",
      "start_line": 45,
      "end_line": 52,
      "severity": "critical",
      "category": "security",
      "title": "SQL Injection Vulnerability",
      "description": "User input is directly concatenated into SQL query without parameterization",
      "suggestion": "Use parameterized queries or prepared statements",
      "code_snippet": "cursor.execute(f\"SELECT * FROM users WHERE username = '{username}'\")",
      "suggested_code": "cursor.execute(\"SELECT * FROM users WHERE username = %s\", (username,))",
      "rationale": "Parameterized queries prevent SQL injection attacks by separating SQL code from data"
    }
  ],
  "positives": [
    "Good error handling with try/catch blocks",
    "Clear function naming and documentation",
    "Appropriate use of logging for debugging"
  ],
  "recommendations": [
    "Consider adding unit tests for the authentication logic",
    "Implement rate limiting to prevent brute force attacks"
  ]
}
```
