from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import os
import re
from datetime import datetime
import PyPDF2
import docx

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'docx', 'txt'}

# Create uploads folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def extract_text_from_pdf(file_path):
    """Extract text from PDF file"""
    text = ""
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text()
    except Exception as e:
        print(f"Error reading PDF: {e}")
    return text

def extract_text_from_docx(file_path):
    """Extract text from DOCX file"""
    text = ""
    try:
        doc = docx.Document(file_path)
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
    except Exception as e:
        print(f"Error reading DOCX: {e}")
    return text

def extract_text_from_txt(file_path):
    """Extract text from TXT file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        print(f"Error reading TXT: {e}")
        return ""

def extract_text(file_path):
    """Extract text based on file extension"""
    extension = file_path.rsplit('.', 1)[1].lower()
    if extension == 'pdf':
        return extract_text_from_pdf(file_path)
    elif extension == 'docx':
        return extract_text_from_docx(file_path)
    elif extension == 'txt':
        return extract_text_from_txt(file_path)
    return ""

def analyze_resume(text):
    """Analyze resume and return ratings and feedback"""
    text_lower = text.lower()
    
    # Initialize scores
    scores = {
        'contact_info': 0,
        'experience': 0,
        'education': 0,
        'skills': 0,
        'keywords': 0,
        'formatting': 0
    }
    
    feedback = []
    
    # Check for contact information (email, phone)
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    phone_pattern = r'(\+?\d{1,3}[-.\s]?)?(\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}'
    
    if re.search(email_pattern, text):
        scores['contact_info'] += 50
    else:
        feedback.append("❌ Missing email address")
    
    if re.search(phone_pattern, text):
        scores['contact_info'] += 50
    else:
        feedback.append("❌ Missing phone number")
    
    # Check for experience section
    experience_keywords = ['experience', 'work history', 'employment', 'professional experience']
    if any(keyword in text_lower for keyword in experience_keywords):
        scores['experience'] += 40
        # Check for dates and job titles
        if re.search(r'\b(20\d{2}|19\d{2})\b', text):
            scores['experience'] += 30
        if len(text) > 500:  # Has substantial content
            scores['experience'] += 30
    else:
        feedback.append("❌ No clear experience section found")
    
    # Check for education
    education_keywords = ['education', 'academic', 'university', 'college', 'degree', 'bachelor', 'master', 'phd']
    if any(keyword in text_lower for keyword in education_keywords):
        scores['education'] += 60
        if re.search(r'\b(20\d{2}|19\d{2})\b', text):
            scores['education'] += 40
    else:
        feedback.append("❌ No education section found")
    
    # Check for skills
    skills_keywords = ['skills', 'technical skills', 'competencies', 'proficiencies']
    tech_skills = ['python', 'java', 'javascript', 'c++', 'sql', 'html', 'css', 'react', 
                   'node', 'angular', 'aws', 'azure', 'docker', 'kubernetes', 'git']
    
    if any(keyword in text_lower for keyword in skills_keywords):
        scores['skills'] += 40
    
    tech_count = sum(1 for skill in tech_skills if skill in text_lower)
    if tech_count > 0:
        scores['skills'] += min(60, tech_count * 10)
    else:
        feedback.append("⚠️ Consider adding technical skills")
    
    # Check for action keywords (good resume practices)
    action_words = ['developed', 'managed', 'led', 'created', 'implemented', 'designed',
                    'improved', 'increased', 'reduced', 'achieved', 'delivered']
    keyword_count = sum(1 for word in action_words if word in text_lower)
    scores['keywords'] = min(100, keyword_count * 15)
    
    if keyword_count < 3:
        feedback.append("⚠️ Use more action verbs (developed, managed, led, etc.)")
    
    # Check formatting (basic checks)
    lines = text.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    
    if len(text) > 300:
        scores['formatting'] += 30
    if len(non_empty_lines) > 10:
        scores['formatting'] += 30
    if text.strip():  # Not just whitespace
        scores['formatting'] += 40
    
    # Calculate overall score
    overall_score = sum(scores.values()) / len(scores)
    
    # Add positive feedback
    if scores['contact_info'] == 100:
        feedback.append("✅ Complete contact information")
    if scores['experience'] >= 80:
        feedback.append("✅ Strong experience section")
    if scores['education'] >= 80:
        feedback.append("✅ Education details present")
    if scores['skills'] >= 80:
        feedback.append("✅ Good skills coverage")
    if keyword_count >= 5:
        feedback.append("✅ Strong use of action verbs")
    
    # Generate rating
    if overall_score >= 85:
        rating = "Excellent"
        color = "success"
    elif overall_score >= 70:
        rating = "Good"
        color = "info"
    elif overall_score >= 50:
        rating = "Fair"
        color = "warning"
    else:
        rating = "Needs Improvement"
        color = "danger"
    
    return {
        'overall_score': round(overall_score, 1),
        'rating': rating,
        'color': color,
        'scores': scores,
        'feedback': feedback,
        'word_count': len(text.split())
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'resume' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['resume']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Please upload PDF, DOCX, or TXT'}), 400
    
    # Save file
    filename = secure_filename(file.filename)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{timestamp}_{filename}"
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)
    
    # Extract and analyze
    text = extract_text(file_path)
    
    if not text.strip():
        os.remove(file_path)  # Clean up
        return jsonify({'error': 'Could not extract text from file'}), 400
    
    analysis = analyze_resume(text)
    
    # Clean up uploaded file
    os.remove(file_path)
    
    return jsonify(analysis)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
