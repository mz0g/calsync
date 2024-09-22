from flask import Flask, request, redirect, url_for, render_template
import subprocess
import os

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        link = request.form['link']
        class_name = request.form['class_name']
        # Run scrapper.py with the provided link and class name
        result = subprocess.run(
            ['python3', os.path.join(os.path.dirname(__file__), 'scrapper.py'), link, class_name],
            capture_output=True,
            text=True
        )
        print(result.stdout)
        print(result.stderr)

        # Check if the upload was successful (assuming 0 return code means success)
        if result.returncode == 0:
            return redirect(url_for('success'))
        else:
            return redirect(url_for('error', message=result.stderr.strip()))  # Pass the error message

    return render_template('index.html')

@app.route('/success')
def success():
    return render_template('success.html')

@app.route('/error')
def error():
    message = request.args.get('message', 'An unknown error occurred.')
    return render_template('error.html', message=message)

if __name__ == '__main__':
    app.run(debug=True)
