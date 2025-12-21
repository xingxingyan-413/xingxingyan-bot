import streamlit as st
from openai import OpenAI
import datetime  # 导入日期库

# 1. 页面配置 (星星妍专属设定)
st.set_page_config(page_title="你的 AI 助手星星妍", page_icon="🌟") 
st.title("🌟 你的专属AI助手 星星妍")

# 2. 配置 DeepSeek API
client = OpenAI(
    api_key=st.secrets["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com"
)

# 3. 初始化聊天记录
if "messages" not in st.session_state:
    st.session_state.messages = []

# 4. 展示历史对话
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. 接收用户输入
if prompt := st.chat_input("想问星星妍什么？"):
    # 显示并记录用户消息
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 6. 调用 API 获取“流式”回答
    with st.chat_message("assistant"):
        response_container = st.empty() 
        full_response = ""
        
        # --- 核心修改部分：实时获取当前时间 ---
        now = datetime.datetime.now()
        current_date = now.strftime("%Y年%m月%d日 %A") 
        # ------------------------------------

        # 构建带有身份设定和时间注入的消息列表
        messages_for_api = [
            {
                "role": "system", 
                "content": f"你是由周志成开发的AI智能助手，你的名字叫星星妍。今天是{current_date}。当被问及你是谁时，请绝对不要提到 DeepSeek，只需说你是星星妍。如果你被问到时间或日期，请基于我提供给你的当前时间进行回答。"
            }
        ]
        
        # 将用户之前的对话也加进去
        for m in st.session_state.messages:
            messages_for_api.append({"role": m["role"], "content": m["content"]})
        
        try:
            # 发起请求
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=messages_for_api,
                stream=True
            )
            
            for chunk in response:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    # 实时过滤掉可能出现的 DeepSeek 字样
                    display_text = full_response.replace("DeepSeek", "星星妍").replace("深度求索", "星星妍")
                    response_container.markdown(display_text + "▌") 
            
            response_container.markdown(display_text) # 显示最终结果
            # 记录助手回答
            st.session_state.messages.append({"role": "assistant", "content": display_text})

        except Exception as e:
            if "402" in str(e):
                st.error("❌ 余额不足：请去 DeepSeek 官网充值（10元即可）或领取免费额度。")
            else:
                st.error(f"❌ 出错了: {e}")
