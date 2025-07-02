from flask import Flask, render_template, request, redirect, url_for, session
import random
from sympy import isprime

app = Flask(__name__)
app.secret_key = 'secretkey123'

# Generate all 5-digit primes once
FIVE_DIGIT_PRIMES = [str(num) for num in range(10000, 100000) if isprime(num)]
MAX_ATTEMPTS = 10
WORD_LENGTH = 5


def get_feedback(guess, target):
    feedback = []
    for i in range(len(guess)):
        if guess[i] == target[i]:
            feedback.append('correct')
        elif guess[i] in target:
            feedback.append('present')
        else:
            feedback.append('absent')
    return feedback


@app.route('/', methods=['GET', 'POST'])
def index():
    if 'target' not in session:
        session['target'] = random.choice(FIVE_DIGIT_PRIMES)
        session['attempts'] = []

    message = ''
    hint = ''

    if request.method == 'POST':
        guess = request.form['guess']
        if not guess.isdigit() or len(guess) != 5 or not isprime(int(guess)):
            message = 'Enter a valid 5-digit prime number.'
        else:
            feedback = get_feedback(guess, session['target'])
            session['attempts'].append({'guess': guess, 'feedback': feedback})
            session.modified = True
            if guess == session['target']:
                return redirect(url_for('win'))
            elif len(session['attempts']) >= MAX_ATTEMPTS:
                return redirect(url_for('lose'))

    return render_template('index.html', attempts=session['attempts'], message=message, hint=hint)


@app.route('/hint')
def get_hint():
    if len(session.get('attempts', [])) < 3:
        hint = "Hints unlock after 3 attempts!"
    else:
        target = session['target']
        guessed_positions = {i for attempt in session['attempts'] for i, f in enumerate(attempt['feedback']) if f == 'correct'}
        unrevealed = [i for i in range(WORD_LENGTH) if i not in guessed_positions]
        if unrevealed:
            idx = random.choice(unrevealed)
            hint = f"Digit {idx + 1} is {target[idx]}."
        else:
            hint = "You've already revealed all digits!"
    return redirect(url_for('index', hint=hint))


@app.route('/win')
def win():
    target = session['target']
    session.clear()
    return render_template('result.html', result="You guessed the number! 🎉", target=target)


@app.route('/lose')
def lose():
    target = session['target']
    session.clear()
    return render_template('result.html', result="Out of attempts!", target=target)


if __name__ == '__main__':
    app.run(debug=True)
