
#Import necessary libraries

import pandas as pd
import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import requests
from sqlalchemy import create_engine
from io import StringIO  # Import StringIO directly from the io module
from io import BytesIO
from datetime import datetime
#from supabase import create_client, Client
from supabase.client import ClientOptions
import gspread
from google.oauth2 import service_account
import json
import numpy as np
import boto3
from botocore.exceptions import NoCredentialsError
import urllib.parse
from dotenv import load_dotenv
load_dotenv()



# AWS credentials setup
import os

# Use environment variables for AWS credentials
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
s3_bucket_name = os.getenv('BUCKET_NAME')
# os.environ['AWS_DEFAULT_REGION'] = 'your_preferred_region'

# Configure boto3 with the credentials
boto3.setup_default_session(
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)

def upload_to_s3(file, bucket_name, s3_file_name):
    s3 = boto3.client('s3')
    try:
        s3.upload_fileobj(file, bucket_name, s3_file_name)
        return True
    except NoCredentialsError:
        st.error("AWS credentials not available")
        return False
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return False




# Function to get the current timestamp
def get_timestamp():
    return datetime.now()

# Display the PNG image in the top left corner of the Streamlit sidebar with custom dimensions
image_path = 'https://twetkfnfqdtsozephdse.supabase.co/storage/v1/object/sign/stemcheck/VS-logo.png?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1cmwiOiJzdGVtY2hlY2svVlMtbG9nby5wbmciLCJpYXQiOjE3MjE5NzA3ODUsImV4cCI6MTc1MzUwNjc4NX0.purLZOGk272W80A4OlvnavqVB9u-yExhzpmI3dZrjdM&t=2024-07-26T05%3A13%3A02.704Z'
st.markdown(
    f'<div style="text-align:center"><img src="{image_path}" width="150"></div>',
    unsafe_allow_html=True
)

st.markdown(
    "<div style='text-align: center;margin-bottom: 30px;'>"
    "<span style='font-size: 34px; font-weight: bold;'>Join 'She for STEM' Movement</span><br>"
    "<span style='font-size: 22px;font-weight: bold;'>Sign up to shape the future of next generation in STEM</span>"
    "</div>", 
    unsafe_allow_html=True
)

Name=st.text_input("Enter your full name*")
Email_id=st.text_input("Enter your email address (Work/Personal)*")
Number=st.text_input("Enter your WhatsApp number (with country code, DONOT ADD '+')*")
Profile=st.text_input("Enter your LinkedIn profile link here")
Institute=st.text_input("Enter your current Institute/University/Organization*")
Current_job=st.text_input("Current Job title/Designation")
Degree = st.selectbox('Highest degree obtained*',("B.Sc.","M.Sc.","B.E./B.Tech.","M.Tech.","B.Pharm.","M.Pharm.","MBA","Ph.D."))
primary_key = f"{Number}_{Name}"

country_names = ["Afghanistan","Albania","Algeria","Andorra","Angola","Antigua and Barbuda","Argentina","Armenia","Australia","Austria","Azerbaijan","The Bahamas","Bahrain","Bangladesh","Barbados","Belarus","Belgium","Belize","Benin",
"Bhutan","Bolivia","Bosnia and Herzegovina","Botswana","Brazil","Brunei","Bulgaria","Burkina Faso","Burundi","Cabo Verde","Cambodia","Cameroon",
"Canada","Central African Republic","Chad","Chile","China","Colombia","Comoros","Congo, Democratic Republic of the Congo", "Republic of the","Costa Rica",
"Côte d’Ivoire","Croatia","Cuba","Cyprus","Czech Republic","Denmark",
"Djibouti","Dominica","Dominican Republic","East Timor (Timor-Leste)","Ecuador","Egypt","El Salvador","Equatorial Guinea","Eritrea","Estonia","Eswatini",
"Ethiopia","Fiji","Finland","France","Gabon","The Gambia","Georgia","Germany","Ghana","Greece","Grenada","Guatemala","Guinea","Guinea-Bissau","Guyana"
"Haiti","Honduras","Hungary","Iceland","India","Indonesia","Iran","Iraq","Ireland","Israel","Italy","Jamaica","Japan","Jordan","Kazakhstan","Kenya",
"Kiribati","Korea", "North Korea", "South Kosovo","Kuwait","Kyrgyzstan","Laos","Latvia","Lebanon","Lesotho","Liberia","Libya","Liechtenstein","Lithuania",
"Luxembourg","Madagascar","Malawi","Malaysia","Maldives","Mali","Malta","Marshall Islands","Mauritania","Mauritius","Mexico","Micronesia, Federated States of","Moldova",
"Monaco","Mongolia","Montenegro","Morocco","Mozambique","Myanmar (Burma)","Namibia","Nauru","Nepal","Netherlands","New Zealand","Nicaragua","Niger",
"Nigeria","North Macedonia","Norway","Oman","Pakistan","Palau","Panama","Papua New Guinea","Paraguay","Peru","Philippines","Poland","Portugal",
"Qatar","Romania","Russia","Rwanda","Saint Kitts and Nevis","Saint Lucia","Saint Vincent and the Grenadines","Samoa","San Marino","Sao Tome and Principe","Saudi Arabia",
"Senegal","Serbia","Seychelles","Sierra Leone","Singapore","Slovakia","Slovenia","Solomon Islands","Somalia","South Africa","Spain","Sri Lanka",
"Sudan","Suriname","Swaziland","Sweden","Switzerland","Syria","Taiwan","Tajikistan","Tanzania","Thailand","Togo","Tonga","Trinidad and Tobago","Tunisia",
"Turkey","Turkmenistan","Tuvalu","Uganda","Ukraine","United Arab Emirates","United Kingdom","United States","Uruguay","Uzbekistan","Vanuatu",
"Vatican City","Venezuela","Vietnam","Yemen","Zambia","Zimbabwe"]

Country=st.selectbox('Country you currently reside in*',country_names)
Current_city=st.text_input("Your current city*")

options = ['English','Hindi','Marathi','Malayalam','Kannada','Telgu','Assamese','Bengali','Gujarati','Manipuri','Tamil','Odia','Punjabi','Urdu','Maithili','Konkani','Kashmiri']
selected_options = st.multiselect("What communication languages are you comfortable in? * ", options)

comments=['Inspirational female role model for young women in STEM| You will\n share your personal & professional journey in STEM|\n Virtual engagement| 1.5 hours 1-2 times a year','Mentor|Help fellows advance their STEM skills through innovative & frugal\nhands-on projects|Virtual engagement|\n 3 hours per week for 12-14 weeks once a year','Tech Capstone Project/Research Project Developers| Design challenging hands on projects for fellows to elicit critical thinking| Virtual engagement |atleast 2-3 hours per week/1 month']
comments_a=st.selectbox("How would you like to join VigyanShaala's #SheforSTEM movement?*",comments)

option2 = st.radio("How many years have you worked as a STEM professional?*", ("2-3 years","4-6 years","7-10 years"," More than 10 years"))
#Time=["Thursday | 3:00 - 4:30 PM IST","Friday | 3:00 - 4:30 PM IST","Saturday | 10:00 - 11:30 AM IST","Saturday | 3:00 - 4:30 PM IST","Saturday | 4:00 - 5:30 PM IST","Saturday | 6:00 - 7:30 PM IST"]
#session_times=st.multiselect("Do you have any preferred days and times for these sessions? Please select all that apply*",Time)
option_B = st.radio(" Would you like to schedule a 10-15 minute call with us for understanding the structure/content of your talk?*",("Yes","No","Maybe"))

#uploaded_file = st.file_uploader("Upload a file", type=["csv", "txt"])
uploaded_file1 = st.file_uploader(" Upload your Curriculum Vitae/Resume*", accept_multiple_files=False, type=["pdf", "txt"])
if uploaded_file1 is not None:  
    # Define the folder name and S3 file path
    folder_name = "cv_resume"
    s3_file_name = f"{folder_name}/{uploaded_file1.name}"
    s3_bucket_name = s3_bucket_name  # replace with your actual bucket name

    # Upload file to S3
    if upload_to_s3(uploaded_file1, s3_bucket_name, s3_file_name):
        st.success("Curriculum Vitae/Resume uploaded successfully.")

        # Encode the file name in the URL to handle spaces and other special characters
        encoded_file_name = urllib.parse.quote(uploaded_file1.name)
        encoded_folder_name = urllib.parse.quote(folder_name)
        
        # Construct the URL to the uploaded file
        file_url_1 = f"https://{s3_bucket_name}.s3.ap-south-1.amazonaws.com/{encoded_folder_name}/{encoded_file_name}"
        st.write(f"[Access your uploaded file]({file_url_1})")
    else:
        st.error("Failed to upload sample work to S3. Please try again.")
else:
    st.warning("No file uploaded for sample work.")

   
#uploaded_file = st.file_uploader("Upload a file", type=["csv", "txt"])
uploaded_file2 = st.file_uploader(" Please upload your bio and a professional headshot", accept_multiple_files=False, type=["pdf", "txt","png","jpg","jpeg"])
if uploaded_file2 is not None:
    # Define the folder name and S3 file path
    folder_name = "Bio and a professional headshot"
    s3_file_name = f"{folder_name}/{uploaded_file2.name}"
    s3_bucket_name = s3_bucket_name  # replace with your actual bucket name

    # Upload file to S3
    if upload_to_s3(uploaded_file2, s3_bucket_name, s3_file_name):
        st.success("Bio and a professional headshot uploaded successfully.")

        # Encode the file name in the URL to handle spaces and other special characters
        encoded_file_name = urllib.parse.quote(uploaded_file2.name)
        encoded_folder_name = urllib.parse.quote(folder_name)
        
        # Construct the URL to the uploaded file
        file_url_2 = f"https://{s3_bucket_name}.s3.ap-south-1.amazonaws.com/{encoded_folder_name}/{encoded_file_name}"
        st.write(f"[Access your uploaded file]({file_url_2})")
    else:
        st.error("Failed to upload sample work to S3. Please try again.")
else:
    file_url_2 = "Not uploaded"


if not Name or not Email_id or not Number or not Institute or not Degree or not Country or not Current_city or not selected_options or not comments_a or not option2 or not option_B or not uploaded_file1:
    st.error("Please fill in all the compulsory fields marked with * before proceeding.")
    st.stop()


def create_feedback_dataframe(primary_key, Name, Email_id, Number, Profile, Institute, Current_job, Degree, Country, Current_city, selected_options, comments_a,option2,option_B,file_url_1,file_url_2):
    data = {
        'ID': primary_key,
        'Enter your full name *': Name,
        'Enter your email address *':Email_id ,
        "Enter your WhatsApp number (with country code, DONOT ADD '+') *":Number,
        'Enter your LinkedIn profile link here': Profile,
        'Enter your current Institute/University/Organization *':Institute,
        'Current Job title/Designation': Current_job ,
        'Highest degree obtained *':Degree ,
        'Country you currently reside in *': Country,
        'Your current city *':Current_city ,
        'What communication languages are you comfortable in?  *': selected_options,
        "How would you like to join VigyanShaala's #SheforSTEM movement?": comments_a,
        'How many years have you worked as a STEM professional? *': option2,
        #'Do you have any preferred days and times for these sessions? Pl': session_times,
        'Would you like to schedule a 10-15 minute call with us for unde': option_B,
        'Upload your Curriculum Vitae/Resume *': file_url_1,  # Add file name or None if no file
        'Please upload your bio and a professional headshot': file_url_2  # Same for second file
    }

    feedback_df = pd.DataFrame([data])
    return feedback_df



combined_button_text = "Submit"   

if st.button(combined_button_text):
    feedback_df = create_feedback_dataframe(primary_key, Name, Email_id, Number, Profile, Institute, Current_job, Degree, Country, Current_city, selected_options, comments_a,option2,option_B,file_url_1,file_url_2)

    # Prepare the JSON data
    json_data = feedback_df[[ 'Enter your full name *', 'Enter your email address *',"Enter your WhatsApp number (with country code, DONOT ADD '+') *", 'Enter your LinkedIn profile link here', 'Enter your current Institute/University/Organization *','Current Job title/Designation','Highest degree obtained *','Country you currently reside in *','Your current city *','What communication languages are you comfortable in?  *',"How would you like to join VigyanShaala's #SheforSTEM movement?",'How many years have you worked as a STEM professional? *','Would you like to schedule a 10-15 minute call with us for unde','Upload your Curriculum Vitae/Resume *','Please upload your bio and a professional headshot','ID']].to_dict(orient='records')[0]
    feedback_df = feedback_df.applymap(lambda x: ', '.join(x) if isinstance(x, list) else x)

    # AWS RDS database connection info
    DB_USERNAME=os.getenv('DB_USERNAME')
    DB_PASSWORD=os.getenv('DB_PASSWORD')
    DB_NAME=os.getenv('DB_NAME')
    DB_PORT=os.getenv('DB_PORT')
    DB_ENDPOINT=os.getenv('DB_ENDPOINT')



    # Create the connection string
    engine_str = f"mysql+mysqlconnector://{DB_USERNAME}:{DB_PASSWORD}@{DB_ENDPOINT}:{DB_PORT}/{DB_NAME}"

    # Create the SQLAlchemy engine
    engine = create_engine(engine_str)
    

    # Store the DataFrame in the database table
    table_name = 'Mentor_Recruitment'  # Replace with your table name
    feedback_df.to_sql(table_name, con=engine, if_exists='append', index=False)
    st.success('Thankyou for your response.')
