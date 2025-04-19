from flask import Flask, render_template, request, redirect, url_for, session
import json
import random

app = Flask(__name__)
app.secret_key = 'supersecretkey'

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        captcha_answer = request.form['captcha_answer']
        expected_captcha = session.get('captcha_result')

        if not expected_captcha or int(captcha_answer) != expected_captcha:
            return render_template('login.html', error="Incorrect CAPTCHA.", captcha_question=session.get('captcha_question'))

        session['email'] = email
        session['username'] = username
        session['question_index'] = 0
        session['answers'] = []
        return redirect(url_for('quiz'))

    # CAPTCHA generation
    num1, num2 = random.randint(1, 9), random.randint(1, 9)
    captcha_question = f"What is {num1} + {num2}?"
    session['captcha_result'] = num1 + num2
    session['captcha_question'] = captcha_question

    return render_template('login.html', captcha_question=captcha_question)

@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    if 'email' not in session:
        return redirect(url_for('login'))

    with open('questions.json') as f:
        questions = json.load(f)

    question_index = session.get('question_index', 0)

    if question_index >= len(questions):
        return redirect(url_for('submit'))

    question = questions[question_index]
    return render_template('quiz.html', question=question, question_index=question_index, total_questions=len(questions))

@app.route('/next_question', methods=['POST'])
def next_question():
    if 'email' not in session:
        return redirect(url_for('login'))

    user_answer = request.form.get('answer')
    question_index = session.get('question_index', 0)
    answers = session.get('answers', [])
    answers.append(user_answer)
    session['answers'] = answers
    session['question_index'] = question_index + 1
    return redirect(url_for('quiz'))

@app.route('/submit', methods=['POST', 'GET'])
def submit():
    if 'email' not in session:
        return redirect(url_for('login'))

    with open('questions.json') as f:
        questions = json.load(f)

    score = 0
    user_answers = session['answers']
    detailed_results = []

    for i, (user_ans, q) in enumerate(zip(user_answers, questions)):
        correct = user_ans == q['answer']
        if correct:
            score += 1
        detailed_results.append({
            "question": q['question'],
            "options": q['options'],
            "user_answer": user_ans,
            "correct_answer": q['answer'],
            "is_correct": correct
        })

    return render_template(
        'result.html',
        score=score,
        total=len(questions),
        username=session['username'],
        results=detailed_results
    )


@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/review')
def review():
    if 'email' not in session:
        return redirect(url_for('login'))

    with open('questions.json') as f:
        questions = json.load(f)

    user_answers = session.get('answers', [])
    detailed_results = []

    for user_ans, q in zip(user_answers, questions):
        detailed_results.append({
            "question": q['question'],
            "options": q['options'],
            "user_answer": user_ans,
            "correct_answer": q['answer'],
            "is_correct": user_ans == q['answer']
        })

    return render_template('review.html', username=session['username'], results=detailed_results)


if __name__ == '__main__':
    app.run(debug=True)
