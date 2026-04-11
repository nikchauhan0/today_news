from flask import Flask, render_template, request, redirect, jsonify
import time
import requests
from bs4 import BeautifulSoup
import random
import google.generativeai as genai
import json
import os
import hashlib
from dotenv import load_dotenv


load_dotenv()
api = os.getenv("API_KEY")

app=Flask(__name__)
news_dict = {}
@app.route('/')
def news():
    r=requests.get('https://timesofindia.indiatimes.com/india')
    soup=BeautifulSoup(r.content,'html.parser')
    elements=soup.find_all(class_='IhGTd')
    
    news_list=[]


    # for index,element in enumerate(elements,start=1):
    for element in elements:
        text = element.get_text(strip=True)
        news_id = hashlib.md5(text.encode()).hexdigest()
        news_dict[news_id] = text
        news_list.append((news_id,text))
        print(f"news list:{news_list}")

        
        # headline=index,element.get_text(strip=True)
   
        # new_list.append({'index':index,'headline':headline})
        
    return render_template('headlines.html',news= news_list)



@app.route('/article/<news_id>')
def article(news_id):
    genai.configure(api_key=api)
    model = genai.GenerativeModel('gemini-2.5-flash-lite')

    news_item = news_dict.get(news_id )
    prompt = f"""
Write a fully factual news article about the following headline:

{news_item}

You must perform web search before writing and use information only from official sources such as government websites official organization or company websites official press release pages or official regulatory authorities.

All facts must be verified from at least two official sources. If official verification is not available clearly state that official confirmation is unavailable and stop the article.

Write a single continuous article of at least 150 words.
Do not use asterisks anywhere in the output.
Do not use bullet points.
Do not use star characters.
Do not use hyphen signs.
Do not include assumptions rumors anonymous claims or vague phrases.
Include names dates locations titles numbers and quotes only if they are explicitly present on official sources.
If official sources show conflicting information mention both values and clearly state which source reports what.

Start with a clear and crisp headline.s
Then write a short introduction giving context.
Then explain what happened when it happened where it happened and who officially confirmed it.
Then explain the real world impact on people users students customers or the public.

End with a Sources section listing only official source names and their domains without full URLs and briefly mention what fact each source confirmed.
"""

    try:
        response = model.generate_content(prompt)
        article = response.text 
    except Exception as e:
        return f"ERROR: {e}"

    return render_template('articles.html',article=article,title=news_item)

if __name__=="__main__":
    app.run()
