import ollama


messages = []
while True:
    user_input = input("User: ")
    if user_input.strip().lower() in ("exit", "quit"):
        break

    messages.append({"role": "user", "content": user_input})

    response = ollama.chat(model="llama3.1:8b", messages=messages)

    reply = response["message"]["content"]
    messages.append({"role": "assistent", "content": reply})

    print("\nGante: ", reply)
