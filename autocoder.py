#/usr/bin/env python3

# print a welcome message
print("\n### Welcome to the autocoder!\n")

import subprocess
import requests
import json

# Function to make an HTTP POST request to the OpenAI completion endpoint
def query_ai(description, feedback="", iteration=1):
    api_url = "https://api.openai.com/v1/chat/completions"
    api_key = "OPENAI_API_KEY"  # Replace with your actual OpenAI API key

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    prompt_text = f"""
    Your response must be python code only, only comment you might have must be in comment syntax because 
    your response will be directly used as runnable code. Create a Python program based on the following
    description: \"{description}\".
    This is the iteration number {iteration} of the code generation process.
    If this not the first iteration, the following is the output from the last program execution (called with `python` in `zsh` on macOS): \"{feedback}\".
    If you reason that your code is not correct, respond with a modified version of the code. If you think the code is correct, try to come up with your
    own improvement ideas of error handling, logging and optimization . If you are satisfied with the code, respond with the code as is.
    \n\n###\n\n
    """

    data = {
        "model": "gpt-4-1106-preview",  # or another model version
        "messages": [{"role": "user", "content": prompt_text}],
        "temperature": 0.5,
        "top_p": 1.0,
        "frequency_penalty": 0.0,
        "presence_penalty": 0.0,
        "stop": ["###"]
    }

    try:
        response = requests.post(api_url, headers=headers, json=data)
        response.raise_for_status()  # This will raise an HTTPError if the response was an error

        response_data = response.json()

        # Print the formatted JSON response
        # print(json.dumps(response_data, indent=4))

        generated_content = response_data.get("choices", [{}])[0].get("message", {}).get("content", "")
        
        # Extracting the code from the content. Assuming the code is enclosed in ```python ... ```
        start_code = generated_content.find("```python") + len("```python\n")
        end_code = generated_content.find("```", start_code)
        generated_code = generated_content[start_code:end_code].strip()
        # prepend the code response with the python shebang
        generated_code = "#!/usr/bin/env python3\n" + generated_code
        return generated_code

    except requests.exceptions.HTTPError as http_err:
        print(f"\n### ERROR: HTTP error occurred: {http_err}\n")  # HTTP error
    except requests.exceptions.ConnectionError as conn_err:
        print(f"\n### ERROR: Connection error occurred: {conn_err}\n")  # Connection error
    except requests.exceptions.Timeout as timeout_err:
        print(f"\n### ERROR: Timeout error occurred: {timeout_err}\n")  # Timeout error
    except requests.exceptions.RequestException as req_err:
        print(f"\n### ERROR: Request exception occurred: {req_err}\n")  # Any other request exception
    except Exception as e:
        print(f"\n### ERROR: An unexpected error occurred: {e}\n")  # Any other error

    return "# UNKNOWN ERROR OCCURRED."

def main():
    # e. g. "Print the first 10 numbers of the Fibonacci sequence."
    description = input("Describe the program: ")

    file_name = input("File name for the new program: ")

    # Append '.py' extension if not already present
    if not file_name.endswith('.py'):
        file_name += '.py'

    feedback = ""
    iteration = 0

    cycles = int(input("Number of development cycles: "))

    for cycle in range(cycles):
        iteration += 1
        # Query OpenAI API with the description to generate code
        code = query_ai(description)

        if not code:
            print("\n### Failed to generate code. Please check your API setup.\n")
            break

        # Write the generated code to the specified file
        with open(file_name, 'w') as file:
            file.write(code)
        
        # Make the file executable (for Unix-based systems)
        subprocess.run(["chmod", "+x", file_name])

        # Execute the script and capture output
        result = subprocess.run(["python", file_name], capture_output=True, text=True)
        feedback = result.stdout
        print(f"\n### Output of iteration {iteration}:\n\n{feedback}\n")

        # Placeholder for feedback mechanism
        # (Future: send result.stdout back to ChatGPT)

    print("### Development cycles complete.\n")

if __name__ == "__main__":
    main()
