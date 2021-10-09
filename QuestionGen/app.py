import os
from flask import Flask, request
from pprint import pprint
import nltk
from Questgen import main

app = Flask(__name__)

qg = main.QGen()
ap = main.AnswerPredictor()

@app.route("/")
def hello():
    return "Hello World!"

@app.post('/generate/multiple-choice-question')
def gen_mcq():
  body = request.json

  if body:
    
    if body['snippets'] is None:
      return 'Request must include snippets'
    else:
      
      results = []

      for snippet in body['snippets']:
        statements = snippet.split('\n')
        
        for statement in statements:
          mcqs = qg.predict_mcq({ 'input_text': statement })
          
          for mcq in mcqs['questions']:
            ans = ap.predict_answer({ 'input_text': mcq['context'], 'input_question': mcq['question_statement']})
    
            if mcq['answer'].lower() == ans.lower():
              results.append(mcq)
    
      return { 'questions': results }
  
  else:
    return 'Request must include a body'

if __name__ == '__main__':
    app.run(host = "localhost", port = 8000, debug = False)