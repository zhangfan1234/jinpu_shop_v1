from openai import OpenAI
from pathlib import Path
from zhipuai import ZhipuAI
import json
import base64
from config.goofish_pro_category import category_list

def kimi_chat(api_key, model, content):
    client = OpenAI(
        api_key=api_key,
        base_url="https://api.moonshot.cn/v1",
    )

    completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "你是 Kimi，一个电商专家"},
            {"role": "user", "content": content}
        ],
        temperature=0.3,
    )

    huida = completion.choices[0].message.content
    return huida


# 聊天接口
def zhipu_chat(api_key, model, messages):

    client = ZhipuAI(api_key=api_key)  # 请填写您自己的APIKey
    response = client.chat.completions.create(
      model=model,  # 填写需要调用的模型名称
        messages=[
            {"role": "user", "content": messages},
        ],
        stream=True,
        )

    # 从响应中获取回答内容, 所有结果都拼合为一个字符串
    result = ""
    for chunk in response:
        result += chunk.choices[0].delta.content

    return result
import os
import sys

def get_resource_path(relative_path):
    """获取资源的绝对路径。在打包后，数据文件会被解压到临时目录，而在开发环境中，则使用当前目录。"""
    # 如果程序是打包后的，那么sys._MEIPASS就是临时目录
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
# 阿里通义模型-文档理解
def generate_category(content,category_txt_path=get_resource_path("闲鱼管家类目.txt")):
    client = OpenAI(
        # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
        api_key="sk-864cc3fc656a4433ba45ba4d97a6d30e",
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )
    file_object = client.files.create(file=Path(category_txt_path), purpose="file-extract")
    completion = client.chat.completions.create(
        model="qwen-long",  # 模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
        messages=[
            {'role': 'system', 'content': f'fileid://{file_object.id}'},
            {'role': 'user', 'content': content}
        ]
    )
    ai_resp = json.loads(completion.model_dump_json())
    print(f'【通义千问】数据响应={ai_resp}')
    choices = ai_resp.get('choices') or []
    if len(choices) == 0:
        return '美妆个护/服饰配饰/其他服饰配饰/其他服饰配饰'
    resp_msg = choices[0].get('message') or {}
    content = resp_msg.get('content') or '美妆个护/服饰配饰/其他服饰配饰/其他服饰配饰'
    return content


# 阿里通义模型
def generate_chat_completion(content):
    print(f"【通义千问】阿里通义模型入参content={content}")
    client = OpenAI(
        # api_key=os.getenv("DASHSCOPE_API_KEY"),
        api_key="sk-864cc3fc656a4433ba45ba4d97a6d30e",
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )
    completion = client.chat.completions.create(
        model="qwen-plus",
        messages=[
            {'role': 'system', 'content': 'You are a helpful assistant.'},
            {'role': 'user', 'content': content}
        ],
    )
    print(f"【通义千问】阿里通义模型出参content={completion.model_dump_json()}")
    return completion.choices[0].message.content

# 阿里图形理解接口
def alybl_img_ai(image_path, prompt):
    print(f"【通义千问】阿里图形理解接口入参image_path={image_path}, prompt={prompt}")
    with open(image_path, "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode("utf-8")

        client = OpenAI(
            # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
            # api_key=os.getenv('DASHSCOPE_API_KEY'),
            api_key='sk-864cc3fc656a4433ba45ba4d97a6d30e',
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )
        completion = client.chat.completions.create(
            model="qwen-vl-max-latest",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                        },
                        {"type": "text", "text": prompt},
                    ],
                }
            ],
        )
        print(f"【通义千问】阿里图形理解接口返参={completion}")
        print(f"【通义千问】阿里图形理解接口返参={completion.choices[0].message.content}")
        return completion.choices[0].message.content

if __name__ == '__main__':
    lm_prompt = f"请根据商品的标题和描述,在已有的全部分类中选择一个最符合的分类, 标题为素板宽松日单毛圈棉灰色套头连帽卫衣男原宿高街潮流纯色出口, 描述为素板宽松日单毛圈棉灰色套头连帽卫衣男原宿高街潮流纯色出口\ne5j1n1401, 请从列表中以下几个分类中选择一个: {category_list}, 请输出对应的序号, 从0开始,只返回一个数字, 不做多余的解释。"
    # print(f'入参描述={lm_prompt}')
    resp_content = generate_chat_completion(lm_prompt)
    print(category_list[int(resp_content)])