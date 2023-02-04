from flask import Flask, render_template, redirect, request, url_for, flash, session

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/search')
def search():
    return render_template('search.html')

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=3000)