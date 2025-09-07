import sys
import os
import json
import uuid
import re
from urllib import request, parse, error

def simple_markdown_to_ansi(text):
    """Converts simple markdown (bold, italic, code) to ANSI terminal codes."""
    # Bold
    text = re.sub(r'\*\*(.*?)\*\*', r'\033[1m\1\033[0m', text)
    # Italic
    text = re.sub(r'_(.*?)_', r'\033[3m\1\033[0m', text)
    text = re.sub(r'\*(.*?)\*', r'\033[3m\1\033[0m', text)
    # Code
    text = re.sub(r'`(.*?)`', r'\033[7m\1\033[0m', text)
    return text

def stream_chat(url, message, session_id):
    """Streams a chat response from the given URL."""
    data = json.dumps({
        "action": "sendMessage",
        "sessionId": session_id,
        "chatInput": message
    }).encode('utf-8')
    headers = {'Content-Type': 'application/json'}
    req = request.Request(url, data=data, headers=headers, method='POST')

    try:
        with request.urlopen(req) as response:
            print("Bot: ", end="")
            for line in response:
                try:
                    decoded_line = line.decode('utf-8')
                    data = json.loads(decoded_line)
                    if 'output' in data:
                        formatted_output = simple_markdown_to_ansi(data['output'])
                        print(formatted_output, end="")
                    else:
                        print(decoded_line, end="") # Print as is if no 'output' key
                except json.JSONDecodeError:
                    print(line.decode('utf-8'), end="") # Print as is if not valid JSON
    except error.HTTPError as e:
        print(f"Error: {e}")
        try:
            # Try to read and print the error response from the server
            error_content = e.read().decode('utf-8')
            print("Server response:")
            print(error_content)
        except Exception as read_error:
            print(f"(Failed to read error response: {read_error})")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def main():
    """Main function for the n8n-chat-cli."""
    url = None
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = os.environ.get("N8N_CHAT_URL")

    if not url:
        print("Usage: python main.py <chat_url>")
        print("Or set the N8N_CHAT_URL environment variable.")
        sys.exit(1)

    session_id = str(uuid.uuid4())
    print("Connecting to chat... (type 'exit' to quit)")
    print(f"Session ID: {session_id}")

    while True:
        try:
            message = input("> ")
            if message.lower() == 'exit':
                break
            if message:
                stream_chat(url, message, session_id)
                print() 
        except KeyboardInterrupt:
            print("\nExiting...")
            break

if __name__ == "__main__":
    main()
