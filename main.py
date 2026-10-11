from openai import OpenAI
from config import API_KEY, BASE_URL, MODEL_NAME
from tools import read_code_file
import time

client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

SYSTEM_PROMPT = """
你是代码审查Agent。
任务：审查Python代码，找出bug、逻辑错误、安全风险、代码坏味道。
输出格式：【发现问题】【风险等级：高/中/低】【改进建议+修改代码】

规则：
1. 如果用户输入是本地文件路径，输出标记：[[TOOL:read_code_file(文件路径)]]
2. 如果用户直接粘贴代码，直接输出审查结果，不要输出工具标记。
3. 收到工具返回结果之后，基于工具拿到的代码做审查。
"""

# 大模型调用带重试：最大重试2次
def llm_call_with_retry(messages, max_retry=2):
    attempt = 0
    while attempt <= max_retry:
        try:
            resp = client.chat.completions.create(
                model=MODEL_NAME,
                messages=messages,
                temperature=0.1
            )
            return resp
        except Exception as e:
            attempt +=1
            if attempt > max_retry:
                raise e
            print(f"⚠️ API调用失败，正在第{attempt}次重试...")
            time.sleep(1)

def run_agent():
    print("====代码审查Agent（无LangChain版）====")
    print("①粘贴代码直接审查；②输入文件路径读取文件；输入exit退出\n")
    chat_history = [{"role":"system","content":SYSTEM_PROMPT}]

    while True:
        user_input = input("请输入：").strip()
        if user_input.lower() == "exit":
            print("程序结束")
            break
        if not user_input:
            print("输入不能为空")
            continue

        chat_history.append({"role":"user", "content": user_input})

        try:
            resp = llm_call_with_retry(chat_history)
            ai_reply = resp.choices[0].message.content

            if "[[TOOL:read_code_file(" in ai_reply:
                start = ai_reply.find("[[TOOL:read_code_file(") + len("[[TOOL:read_code_file(")
                end = ai_reply.find(")]]")
                file_path = ai_reply[start:end].strip()
                print(f">>>Agent调用工具读取文件：{file_path}")
                tool_result = read_code_file(file_path)

                chat_history.append({"role":"user", "content":tool_result})
                resp2 = llm_call_with_retry(chat_history)
                final_output = resp2.choices[0].message.content
            else:
                final_output = ai_reply

            print("\n====审查结果====")
            print(final_output)
            print("================\n")
            chat_history.append({"role":"assistant", "content":final_output})

        except Exception as err:
            print(f"\n程序异常：{err}\n")


if __name__ == "__main__":
    run_agent()
