# Resume Reviewer 📄

An intelligent resume reviewer application that analyzes resumes and provides detailed ratings and feedback.

## Features

- 📤 Upload resumes in PDF, DOCX, or TXT format
- 🎯 Get instant analysis with overall score
- 📊 Detailed scoring across 6 categories:
  - Contact Information
  - Experience
  - Education
  - Skills
  - Keywords (action verbs)
  - Formatting
- 💡 Actionable feedback and suggestions
- 🎨 Beautiful, modern UI with drag-and-drop support

## Installation

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application:**
   ```bash
   python app.py
   ```

3. **Open your browser:**
   Navigate to `http://localhost:5000`

## How to Use

1. Open the application in your web browser
2. Click the upload area or drag and drop your resume file
3. Click "Analyze Resume" button
4. View your results with detailed scores and feedback
5. Make improvements based on the suggestions

## Analysis Categories

- **Contact Info**: Checks for email and phone number
- **Experience**: Looks for work history, dates, and substantial content
- **Education**: Verifies educational background and dates
- **Skills**: Identifies technical and professional skills
- **Keywords**: Counts action verbs and strong resume language
- **Formatting**: Evaluates structure and readability

## Requirements

- Python 3.7+
- Flask
- PyPDF2
- python-docx

## Project Structure

```
resume-review/
├── app.py              # Flask backend with analysis logic
├── templates/
│   └── index.html      # Frontend UI
├── uploads/            # Temporary file storage (auto-created)
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## Tips for Better Scores

- ✅ Include complete contact information (email, phone)
- ✅ Use action verbs (developed, managed, led, implemented)
- ✅ Add specific dates for experience and education
- ✅ List relevant technical skills
- ✅ Keep content substantial but focused
- ✅ Ensure proper formatting and structure

## License

MIT License - Feel free to use and modify!
