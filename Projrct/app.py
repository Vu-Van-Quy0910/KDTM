from flask import Flask, render_template, request

app = Flask(__name__)

# Define static questions for each topic
questions_data = {
    "Triết học": [
        {"question": "Ai là người sáng lập triết học Mác?", "options": ["Karl Marx", "Friedrich Engels", "Jean-Paul Sartre", "Immanuel Kant"], "answer": "Karl Marx"},
    ],
    "Chủ nghĩa xã hội": [
        {"question": "Chủ nghĩa xã hội là hệ tư tưởng nào?", "options": ["Chủ nghĩa xã hội khoa học", "Chủ nghĩa xã hội nhân văn", "Chủ nghĩa xã hội hiện đại", "Chủ nghĩa xã hội chủ nghĩa"], "answer": "Chủ nghĩa xã hội khoa học"},
    ],
    "Toán học": [
        {"question": "Kết quả của 5 + 7 là bao nhiêu?", "options": ["11", "12", "13", "14"], "answer": "12"},
    ],
    "Tiếng Anh": [
        {"question": "What is the past tense of 'go'?", "options": ["went", "gone", "going", "will go"], "answer": "went"},
    ]
}

# Define basic and advanced materials for each topic
materials = {
    "Triết học": {
        "basic": "Giới thiệu về Triết học",
        "advanced": "Nghiên cứu về Triết học Mác"
    },
    "Chủ nghĩa xã hội": {
        "basic": "Giới thiệu về Chủ nghĩa xã hội",
        "advanced": "Chủ nghĩa xã hội khoa học nâng cao"
    },
    "Toán học": {
        "basic": "Toán học Cơ bản",
        "advanced": "Giải tích và Đại số Nâng cao"
    },
    "Tiếng Anh": {
        "basic": "Ngữ pháp Tiếng Anh cơ bản",
        "advanced": "Ngữ pháp và Từ vựng Nâng cao"
    }
}

@app.route('/')
def home():
    return render_template('home.html')  # Redirect to home.html for the button

@app.route('/choose_topic')
def choose_topic():
    return render_template('choose_topic.html')  # Show the topic selection page

@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    topic = request.args.get('topic')  # Get topic from URL parameter
    
    if not topic or topic not in questions_data:
        return f"Chủ đề không hợp lệ: {topic}", 404
    
    questions = questions_data.get(topic)  # Get the questions for the selected topic
    
    if request.method == 'POST':
        answers = request.form
        score = 0
        for i, question in enumerate(questions):
            if answers.get(f"q{i}") == question["answer"]:
                score += 1
        
        # Recommend materials based on score
        if score == 0:
            recommendation = f"""
                Tài liệu cơ bản: <b>{materials[topic]['basic']}</b>
            """
        else:
            recommendation = f"""
                Tài liệu nâng cao: <b>{materials[topic]['advanced']}</b>
            """
        
        return render_template('result.html', score=score, total=len(questions), recommendation=recommendation, topic=topic)  # Pass recommendation to the result page
    
    return render_template('quiz.html', questions=questions, topic=topic)  # Show the quiz page

if __name__ == '__main__':
    app.run(debug=True)
