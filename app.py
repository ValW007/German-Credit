from urllib import response
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from flask import Flask, render_template, request #flask is a web framework for Python that allows one to build web application.
import os  
#Setup model for scam check query
import google.generativeai as genai
import requests

#Configure the API key securely
api=os.getenv("MAKERSUITE") #hide api (like a private key/ pw)
genai.configure(api_key= "AIzaSyCFAOkFd5qjen2xJmfrQjbYAq4pb9oz7fI")
model = genai.GenerativeModel ("gemini-1.5-flash")

#Initialiaing Flask app
app = Flask(__name__) 

#Setting up the INDEX PAGE
@app.route("/",methods=["GET","POST"]) #use flask to map to root URL endpoint denoted by "/". #GET = retrieve from server when URL is accessed, #POST = submit a form
#GET from SG to US, and POST is US to SG
def index(): #when "/" is called, generate function called index
        return(render_template("index.html")) # Flask function will look to index.html under templates for the generation

#Function to run the Button at the Front End
@app.route("/check_scam",methods=["GET","POST"])
def check_scam():
        return(render_template("check_scam.html")) #synchronise front and back-end.

#SCAM_CHECK
# Defining the criteria for scam checks
# Function to check domain reputation
def check_domain_reputation(domain):
    # Placeholder for actual domain reputation check
    # You can integrate with a service like Web of Trust (WOT) or similar
    return 5  # Example score

# Function to check website design and content
def check_website_design(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        # Check for professional design and content quality
        if soup.title and len(soup.find_all('p')) > 5:
            return 5  # Example score
        else:
            return 2
    except:
        return 1

# Function to check HTTPS protocol
def check_https(url):
    return 5 if urlparse(url).scheme == "https" else 1

# Function to check contact information
def check_contact_info(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        contact_info = soup.find_all(text=["Contact", "Contact Us", "Email", "Phone"])
        return 5 if contact_info else 1
    except:
        return 1

# Function to compare to legitimate sites
def compare_to_legitimate_sites(url):
    # Placeholder for actual comparison logic
    return 5  # Example score

# Function to rate scam likelihood
def rate_scam_likelihood(content, url):
        domain = urlparse(url).netloc
        domain_score = check_domain_reputation(domain)
        design_score = check_website_design(url)
        https_score = check_https(url)
        contact_score = check_contact_info(url)
        comparison_score = compare_to_legitimate_sites(url)
    
    # Aggregate scores
        total_score = domain_score + design_score + https_score + contact_score + comparison_score
        return min(max(total_score // 5, 1), 10)  # Ensure the score is between 1 and 10

#Setting up SCAM CHECK RESULT page
@app.route("/check_scam_result",methods=["GET","POST"])

#Send URL to Gemini for scam detection
def check_scam_result():    
    # Create a prompt to check if the URL is a scam"
        url = request.form.get("url")
        prompt = f"Rate on a scale from 1-10 if this URL looks like a scam: {url}"
    
     # Get the result from the Gemini model
        try:
                response = model.generate_content(prompt)
                print(response)
        
    # Extract the content from response
                result = response.text  # Adjust based on actual response format from Gemini
        
        # Rate the likelihood of scam
                scam_rating = rate_scam_likelihood(result, url)
                return render_template("check_scam_result.html", r=result, rating=scam_rating)
    
        except Exception as e:
                return f"Error: {str(e)}"

if __name__ == "__main__":
    app.run(debug=True)