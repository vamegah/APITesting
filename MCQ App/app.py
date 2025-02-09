import requests
from flask import Flask, render_template, request

app = Flask(__name__)

# Open Trivia API Categories
CATEGORIES = {
    "General Knowledge": 9,
    "Science & Nature": 17,
    "Computers": 18,
    "Mathematics": 19,
    "Geography": 22,
    "History": 23
}

@app.route('/')
def index():
    return render_template('index.html', categories=CATEGORIES)

@app.route('/quiz', methods=['GET'])
def quiz():
    category_id = request.args.get('category', default=9, type=int)  # Default to General Knowledge
    api_url = f"https://opentdb.com/api.php?amount=5&type=multiple&category={category_id}"
    
    response = requests.get(api_url)
    data = response.json()

    questions_data = {}
    counter = 1  # Manual counter for question numbering

    for item in data['results']:
        question_text = item['question']
        options = item['incorrect_answers'] + [item['correct_answer']]
        options.sort()  # Shuffle options to randomize order

        questions_data[counter] = {  # Assigning question number as a key
            "question": question_text,
            "options": options,
            "correct_answer": item['correct_answer'],
            "option_ids": {option: f"q{counter + i}" for i, option in enumerate(options)}
        }
        counter += 1  # Increment for next question

    return render_template('quiz.html', questions_data=questions_data)


@app.route('/result', methods=['POST'])
def result():
    user_answers = request.form
    score = 0
    total_questions = len(user_answers) // 4  # Since 4 options per question

    for question, data in request.form.items():
        selected_options = request.form.getlist(question)

        # Ensure only one selection per question
        if len(selected_options) == 1:
            selected_answer = selected_options[0]
            original_correct = request.form.get(f"correct_{question}")

            if selected_answer == original_correct:
                score += 1

    return render_template('result.html', score=score, total=total_questions)

if __name__ == '__main__':
    app.run(debug=True)
