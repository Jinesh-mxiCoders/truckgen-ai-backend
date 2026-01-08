# from langchain_openai import ChatOpenAI
# from langchain.memory import ConversationBufferMemory
# from config import settings

# llm = ChatOpenAI(
#     model=settings.OPENAI_MODEL,
#     temperature=0.2
# )

# memory = ConversationBufferMemory(
#     return_messages=True
# )

# def chat_with_memory(system_prompt: str, user_input: str):
#     messages = memory.load_memory_variables({})["history"]

#     response = llm.invoke(
#         messages + [
#             {"role": "system", "content": system_prompt},
#             {"role": "user", "content": user_input}
#         ]
#     )

#     memory.save_context(
#         {"input": user_input},
#         {"output": response.content}
#     )

#     return response.content
