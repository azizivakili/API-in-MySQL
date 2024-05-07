import requests

# Define the API endpoint
api_url = 'http://localhost:8000/get_mcqs'

# Define parameters
params = {
    'test_type': 'BDD',
    'categories': ['Systèmes distribués', 'BDD'],
    'num_questions': 5
}

# Make a GET request to the API
response = requests.get(api_url, params=params)

# Check if the request was successful
if response.status_code == 200:
    mcqs = response.json()
    for index, mcq in enumerate(mcqs, start=1):
        print(f"Question {index}:")
        print(f"Subject: {mcq['subject']}")
        print(f"Question: {mcq['question']}")
        print(f"A: {mcq['responseA']}")
        print(f"B: {mcq['responseB']}")
        print(f"C: {mcq['responseC']}")
        print(f"D: {mcq['responseD']}")
        print("Correct Answer:", mcq['correct'])
        print()
else:
    print("Failed to fetch MCQs. Status code:", response.status_code)
