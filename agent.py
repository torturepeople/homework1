from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage
from tools import read_code_file
from config import API_KEY, BASE_URL, MODEL_NAME


def create_code_review_agent():
    llm = ChatOpenAI(
        api_key=API_KEY,
        base_url=BASE_URL,
        model=MODEL_NAME
    )

    tool_list = [read_code_file]

    system_prompt = """
你是代码审查Agent助手。
你的任务：对Python代码做审查，找出潜在bug、逻辑错误、安全风险、代码坏味道。
输出固定三部分：【发现问题】【风险等级：高/中/低】【改进建议+修改后的代码】

规则：
1. 用户输入本地文件路径，调用read_code_file工具读取代码；
2. 用户直接粘贴代码文本，直接分析，不要调用工具；
3. 如果读取文件报错，直接把错误信息返回用户。
"""

    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content=system_prompt),
        ("placeholder", "{chat_history}"),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}")
    ])

    agent = create_openai_tools_agent(llm, tool_list, prompt)

    agent_executor = AgentExecutor(
        agent=agent,
        tools=tool_list,
        verbose=False,
        handle_parsing_errors=True,
        max_iterations=3
    )
    return agent_executor
