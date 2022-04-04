import os
from jinja2 import Undefined
import pymysql, pymysql.cursors
import json
import hashlib
from Questgen import main
from flask import Flask, request
from threading import Thread, active_count

app = Flask(__name__)

qg = main.QGen()
ap = main.AnswerPredictor()

@app.get('/check')
def hello():
  
    return { 'running': True }

@app.post('/generate/news/multiple-choice-questions')
def gen_mcqs():
  
  print(f'Active threads: {active_count()}')
  body = request.json

  if body:
    
    if body['news_id'] is None:
      return { 'error': 'Request body must include news_id', 'result': None }
    else:
      generator = Generator(body['news_id'])
      generator.daemon = True
      generator.start()
      return { 'result': f'Question generation initiated for news {body["news_id"]}', 'error': None }
  
  else:
    return { 'error': 'Request must include a body', 'result': None }

class Generator(Thread):
  
  def __init__(self, news_id):
    
    Thread.__init__(self)
    self.news_id = news_id
    self.info = json.loads(os.getenv('MYSQL_INFO'))
  
  def run(self):
    news_id = self.news_id
    
    try:
      
      self.snippets_to_mcqs()
      
      print(f'Question generation for news {news_id} completed')
    
    except Exception as ex:
      
      print(f'An exception occurred while generating questions: {ex}')
      
    return
  
  def snippets_to_mcqs(self):
    try:
      news_id = self.news_id
      
      sql = f"select (news_json) from news where news_id='{news_id}'"
      news = self.query(sql)
      news_json = json.loads(news[0]['news_json'])
      
      snippets = [news_json['newsDescription']]
      
      results = []
      
      for snippet in snippets:
        statements = snippet.split('\n')
        
        for statement in statements:
          mcqs = qg.predict_mcq({ 'input_text': statement })
      
          if len(mcqs) > 0:
      
            for mcq in mcqs['questions']:
              ans = ap.predict_answer({ 'input_text': mcq['context'], 'input_question': mcq['question_statement'] })
      
              if mcq['answer'].lower() in ans.lower() or ans.lower() in mcq['answer'].lower():
                mcq.pop('id')
                results.append(mcq)
      
      if len(results) > 0:
        
        names = '(news_question_id, news_id, news_question_json)'
        values = []
        sep = ', '

        for result in results:
        
          result = json.dumps(result)
          hash = hashlib.new('sha256')
          hash.update(result.encode())
          question_id = hash.hexdigest()
          result = result.replace("'", "\\'")
          print('\n', result, '\n')
          values.append(f"('{question_id}', '{news_id}', '{result}')")
        
        values = sep.join(values)
        
        sql = f'insert into news_questions {names} values {values}'
        self.query(sql)
        
    except Exception as ex:
      template = "An exception of type {0} occurred. Arguments:\n{1!r}"
      message = template.format(type(ex).__name__, ex.args)
      print (message)  
      pass  # or you could use 'continue'

  
  def connect(self):
    
    return pymysql.connect(
      
      host = self.info['host'],
      user = self.info['user'],
      password = self.info['password'],
      database = self.info['database'],
      cursorclass = pymysql.cursors.DictCursor
      
    )
  
  def query(self, sql):
    
    result = None
    con = self.connect()
    
    with con:
      with con.cursor() as cursor:
        
        cursor.execute(sql)
        
        if sql.lower().startswith('select'):
          result = cursor.fetchall()
          
      con.commit()
      
    return result

if __name__ == '__main__':
  app.run(port=8000)