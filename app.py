from pywebio.platform.flask import webio_view
from pywebio import STATIC_PATH, config
from flask import Flask, send_from_directory
from pywebio.input import *
from pywebio.output import *
from pywebio import start_server
from urllib.request import urlopen
import sklearn
import time
import pickle
import numpy as np
import pandas as pd
import warnings
import argparse
warnings.filterwarnings(action='ignore')

df_link = urlopen("https://drive.google.com/uc?export=download&id=15tt3FN2Y4dLRyGc12IDKpgsD36Qa-g3z")
model_clf_link = urlopen("https://github.com/RauhanAhmed/loan_app/raw/main/model_clf.pkl")
model_reg_link = urlopen("https://github.com/RauhanAhmed/loan_app/raw/main/model_reg.pkl")

df = pd.read_csv(df_link)
df = df.iloc[0:len(df.index), 1:len(df.columns)]
model_clf = pickle.load(model_clf_link)
model_reg = pickle.load(model_reg_link)

others = ['Education','Transportation','Clothing','Arts','Manufacturing','Construction','Health','Entertainment','Wholesale']

app = Flask(__name__)
df2 = pd.DataFrame()


config(title = "Loan Prediction Application", theme="dark")

def pred(loan_amount, term_in_months, has_male, sector, repayment_interval):
    x = np.zeros(len(df.drop(['funded_amount','funded'],axis=1).columns))
    x[0] = loan_amount
    x[1] = term_in_months
    if has_male == 'Yes':
        x[2] =1
    elif has_male == 'No':
        x[2]=0
    if sector in df.columns:
        i = list(df.drop(['funded','funded_amount'],axis=1).columns).index(sector)
        x[i] = 1
    elif sector in others:
        i = list(df.drop(['funded','funded_amount'],axis=1).columns).index('others')
        x[i] = 1
    if repayment_interval in df.columns:
        i = list(df.drop(['funded','funded_amount'],axis=1).columns).index(repayment_interval)
        x[i] = 1
    df2=pd.DataFrame([list(x)])
    df2.columns = df.drop(['funded','funded_amount'],axis=1).columns
    if model_clf.predict(df2)[0] == 0:
        result = "Sorry you won't be able to get the loan"
    elif model_clf.predict(df2)[0] == 1:
        upper_lim = model_reg.predict([x])[0] + (df['funded_amount'].std()/3)
        if upper_lim > loan_amount:
            upper_lim = loan_amount
            upto = 100
        else:
          upto = (upper_lim/loan_amount)*100
        result = f"You're eligible for a partially funded loan upto {np.round(upto,2)}% that is : Rs.{np.round(upper_lim)}"
    elif model_clf.predict(df2)[0] == 2:
        result = "Congratulations...!!! you're eligible for the loan you applied"
        
    return result

def predict_loan():
    
    with popup("hello everyone...!!!"):
        put_image('https://drive.google.com/uc?export=download&id=1oTHwBSHKNgf1ip_TsdTruk3_ETMdrZ2K')

    
    name = input('Please enter your name :', type=TEXT)
    loan_amount=input('Please enter the Loan Amount(in INR) :', type=NUMBER)
    term_in_months=input('Please enter the loan tenure in months (maximum 60 months) :',type=NUMBER)
    has_male=select('Does the group of borrowers has a male member :',['Yes','No'])
    sector=select('Select the sector for which you want the Loan :',list(df.columns[5:11])+others)
    repayment_interval=select("Select the repayment interval you want :", list(df.columns[12:]))
    
    put_markdown('## Hello {}'.format(name))
    put_processbar('bar')
    for i in range(1, 11):
        set_processbar('bar', i / 10)
        time.sleep(0.1)
    put_text('The loan amount you entered is :', loan_amount,\
             "\nThe loan tenure specified is :", term_in_months,\
             '\nDoes the borrowers has a male member :',has_male,\
             "\nThe sector you applied for is :",sector,\
             "\nThe repayment interval you selected is :",repayment_interval)
    put_text(pred(loan_amount, term_in_months, has_male, sector, repayment_interval))
    put_image(r"https://www.concedro.com/wp-content/uploads/2021/06/money-2724241__340.jpg")
    
    
app.add_url_rule('/calculate', 'webio_view', webio_view(predict_loan),\
                 methods=['GET','POST','OPTIONS'])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p",'--port',type=int, default=2020)
    args=parser.parse_args()
    
    start_server(predict_loan, port = args.port)
