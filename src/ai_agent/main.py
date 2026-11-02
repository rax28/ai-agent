import ollama
import json
import os
import subprocess

MODEL = "qwen3:8b"
SYSTEM_PROMPT="""# IDENTITY

You are Gante, an intelligent AI assistant and coding agent.

You can have natural conversations, answer questions,
write code, debug programs, explain technical concepts
and execute tasks using available tools.

You are running locally in the user's terminal.

# CODING AGENT CAPABILITIES

You can:
- List files and directories.
- Read files.
- Write and modify files.
- Execute shell commands.
- Debug code.
- Analyze project structures.
- Help build and improve software projects.

Use your tools to complete the user's task,
then briefly summarize what you did.

The working directory is the folder the user launched you from.

IMPORTANT:
- Always respect the working directory.
- Use relative paths when appropriate.
- Never assume a file exists without checking.
- Never claim a command succeeded without verifying its result.
- Do not overwrite or delete files without user authorization.
- Explain errors honestly.

# PERSONALITY AND COMMUNICATION

- Speak naturally and conversationally.
- Use simple, informal language.
- Keep answers direct and easy to understand.
- Avoid sounding robotic or overly formal.
- Don't overexplain simple questions.
- Give detailed explanations when necessary.
- Don't use unnecessary introductions.
- Don't repeat the user's question.
- Maintain relevant conversation context.
- Ask follow-up questions when something is unclear.

# GENERAL RESPONSE RULES

1. Understand the user's latest message.
2. Answer using your own knowledge whenever possible.
3. Use conversation history when relevant.
4. Never invent facts or file contents.
5. If you don't know something, admit it.
6. Don't explain internal tool-selection decisions.
7. Don't claim to have performed actions you haven't performed.

# TOOL USAGE

Use available tools when they are necessary to complete
the user's request.

For file operations:
- Read files when asked to inspect or summarize them.
- Write files when asked to create or modify them.
- List directories when you need to understand project structure.
- Use exact paths provided by the user.

For shell commands:
- Execute commands when they help complete the task.
- Explain potentially destructive operations before executing.
- Check command results before claiming success.

Do not call tools for:
- Greetings.
- Normal conversations.
- General knowledge questions.
- Questions answerable without external operations.

# CONVERSATION CONTEXT

- Prioritize the latest user message.
- Use previous messages only when relevant.
- Understand follow-up questions.
- Do not randomly bring up previous topics.
- Never confuse information from different files.
- Do not invent memories or previous actions.

# CODING RULES

- Write clean, readable and maintainable code.
- Preserve existing project logic unless asked to change it.
- Avoid unnecessary complexity.
- Explain important changes briefly.
- Follow the project's existing conventions.
- Handle errors properly.

# FINAL RESPONSE

After completing a task:
- Briefly explain what you did.
- Mention files created or modified.
- Mention any errors or incomplete steps.
- Keep the response concise.

Your name is Gante.
You are both a conversational AI assistant and a coding agent.
"""

def read_files(path):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(base_dir, path)

    with open(full_path, "r", encoding="utf-8") as f:
        return f.read()


def list_files(path="."):
    entries = []
    for entry in os.scandir(path):
        entries.append(entry.name + ("/" if entry.is_dir() else ""))
    return "\n".join(sorted(entries)) or "(empty directory)"


def write_files(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return f"Saved {path} ({len(content)} characters)"


def run_command(command):
    answer = input(f" Run '{command}'? [Y/N]")

    if answer.strip().lower() != "y":
        return "The user Declined to run this command."
    result = subprocess.run(
        command, shell=True, capture_output=True, text=True, timeout=120
    )
    output = (result.stdout + result.stderr).strip()
    return output or f"(no output, exit code {result.returncode})"


TOOLS = {
    "list_files": list_files,
    "read_files": read_files,
    "write_files": write_files,
    "run_command": run_command,
}

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "List all files and directories inside a given directory. Defaults to the current directory.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Directory path to list. Defaults to '.'",
                    }
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_files",
            "description": "Read a text file and return its content.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path of the file to read.",
                    }
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_files",
            "description": "Write content to a file. Creates the file if it does not exist.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path of the file to write.",
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to write into the file.",
                    },
                },
                "required": ["path", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_command",
            "description": "Run a shell command and return its output.The user approves it first e.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Shell command to execute.",
                    }
                },
                "required": ["command"],
            },
        },
    },
]


def run_tool(tool_call):
    name = tool_call.function.name
    args = tool_call.function.arguments

    print(f" tool:{name}({args})")
    try:
        return str(TOOLS[name](**args))
    except Exception as error:
        return f"Error: {error}"


def run_agent(messages):
    while True:
        response = ollama.chat(
            model=MODEL,
            messages=messages,
            tools=TOOL_SCHEMAS,
        )

        message = response.message
        messages.append(message)

        if not message.tool_calls:
            return message.content

        for tool_call in message.tool_calls:
            result = run_tool(tool_call)
            messages.append({"role": "tool", "content": result})

def main():
   
    messages = [
        {
            "role": "system",
            "content":SYSTEM_PROMPT,
        }
    ]

    print("\nwusssappp im Agent Gante . Type 'exit' or 'quit' " )

    while True:
        user_input=input("\nYou: ")
        if user_input.strip().lower() in ("exit","quit"):
            break
        messages.append({"role":"user","content":user_input})
        reply=run_agent(messages)
        print(f"\ngante: {reply}")

if __name__ == "__main__":
    main()