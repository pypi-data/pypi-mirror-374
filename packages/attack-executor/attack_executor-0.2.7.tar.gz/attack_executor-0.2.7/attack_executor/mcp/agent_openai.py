import os
from dotenv import load_dotenv
from openai import OpenAI

# Your server URL (replace with your actual URL)
url = 'https://2db2-73-30-229-139.ngrok-free.app'

load_dotenv()
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key = os.getenv('OPENAI_API_KEY'))

resp = client.responses.create(
    model="gpt-4o",
    tools=[
        {
            "type": "mcp",
            "server_label": "attack-executor-mcp",
            "server_url": f"{url}/mcp/",
            "require_approval": "never",
        },
    ],
    # input="Help me do the penetration testing to the IP address 10.129.99.21",
    input="Roll 6 dices, tell me the result.",
)

print(resp)

# def chat():
#     print("ChatBot (type 'exit' to quit)")
#     messages = [{"role": "system", "content": "You are a helpful assistant."}]

#     while True:
#         user_input = input("You: ")
#         if user_input.lower() == "exit":
#             break

#         messages.append({"role": "user", "content": user_input})

#         try:
#             # response = openai.ChatCompletion.create(
#             #     model="gpt-4o",
#             #     messages=messages
#             # )
#             resp = client.responses.create(
#                     model="gpt-4o",
#                     tools=[
#                         {
#                             "type": "mcp",
#                             "server_label": "attack-executor-mcp",
#                             "server_url": f"{url}/mcp/",
#                             "require_approval": "never",
#                         },
#                     ],
#                     input = messages,
#                 )
#             # reply = response['choices'][0]['message']['content']
#             reply = resp.output_text
#             print("Bot:", reply.strip())

#             messages.append({"role": "assistant", "content": reply})
#         except Exception as e:
#             print("Error:", e)

# if __name__ == "__main__":
#     chat()