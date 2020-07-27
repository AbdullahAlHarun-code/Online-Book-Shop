import os
from flask import Flask, render_template, redirect, request, url_for, flash, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return 'hello mama valo aso'

if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
    	port=int(os.environ.get('PORT')),
    	debug=True)
