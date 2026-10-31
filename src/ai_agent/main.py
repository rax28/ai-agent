import ollama

response = ollama.chat(
    model="llama3.2:latest",
    messages=[
        {
            "role": "user",
            "content": "Hello, how are you?"
        }
    ]

)

print (response["message"]["content"])