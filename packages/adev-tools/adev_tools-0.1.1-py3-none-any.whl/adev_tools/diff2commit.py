import ollama
import sys
from git import Repo

def generate_commit_message(code_changes):
    # Prepare the prompt for CodeLlama
    prompt = f"Generate a concise Git commit message for the following code changes:\n\n{code_changes}\n\nCommit message:"
    
    # Use Ollama to generate a response
    response = ollama.generate(
        model="codellama",  # Specify the model
        prompt=prompt,      # Provide the prompt
        options={
            "temperature": 0.7,  # Adjust creativity (0 = deterministic, 1 = creative)
            "max_tokens": 50     # Limit the length of the response
        }
    )
    
    # Extract and return the generated commit message
    return response["response"].strip()

if __name__ == "__main__":
    # Example code changes
    repo = Repo('.')  # Path to Git repository
    diff_index = repo.git.diff('--cached')
    if diff_index:
    #Generate a commit message using CodeLlama via Ollama
        commit_message = generate_commit_message(diff_index)
        print(commit_message)
        #Commit the changes
        repo.git.commit('-m', commit_message)
    else:
        print("No changes to commit")


