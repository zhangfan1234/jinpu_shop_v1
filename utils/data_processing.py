import utils.api_requests as api
import config.jp_data as jp

def get_ai_result_index_xy(goods_name, goods_detail, lm_texts):
    lm_prompt = f"请根据商品的标题和描述,在已有的几个分类中选择一个最符合的分类, 标题为{goods_name}, 描述为{goods_detail}, 请从列表中以下几个分类中选择一个: {lm_texts}, 请输出对应的序号, 从0开始,只返回一个数字, 不做多余的解释。"
    kimi_key = jp.KIMI_KEY
    kimi_model = jp.KIMI_MODEL
    glm_key = jp.GLM_KEY
    glm_model = jp.GLM_MODEL

    # lm_index = api.zhipu_chat(glm_key, glm_model, lm_prompt)
    lm_index = api.generate_chat_completion(lm_prompt)
    # 判断lm是不是数字, 如果不是则,lm为0
    try:
        lm_index = int(lm_index)
    except:
        lm_index = 0
    return lm_index

def get_ai_result_index(goods_name, goods_detail, lm_texts, img_path_t):
    """
    获取ai返回的属性index结果
    :param ai_result:  ai返回的结果
    :return:  ai返回的属性index结果
    """
    lm_prompt = f"请根据商品的标题和描述,在已有的几个分类中选择一个最符合的分类, 标题为{goods_name}, 描述为{goods_detail}, 请从列表中以下几个分类中选择一个: {lm_texts}, 请输出对应的序号, 从0开始,只返回一个数字, 不做多余的解释。"
    kimi_key = jp.KIMI_KEY
    kimi_model = jp.KIMI_MODEL
    glm_key = jp.GLM_KEY
    glm_model = jp.GLM_MODEL

    # lm_index = api.zhipu_chat(glm_key, glm_model, lm_prompt)
    # img_path_t = img_dir_path + "\\1.jpg"
    lm_index = api.alybl_img_ai(img_path_t, lm_prompt)
    # print("调图片理解模型，返回结果：", lm_index)
    # 判断lm是不是数字, 如果不是则,lm为0
    try:
        lm_index = int(lm_index)
    except:
        lm_index = 0
    return lm_index


def get_ai_input(dict_m, shuxing):
    """
    获取ai返回的属性index结果
    :param ai_result:  ai返回的结果
    :return:  ai返回的属性index结果
    """
    prompt = f"请根据商品的描述信息, 生成一个商品的{shuxing}属性文本，生成的内容最好是只来源于商品描述中的某一个描述，尽可能简单，如果涉及到价格输出纯数字，字数不超过10个字，商品的描述信息为{dict_m}"
    print(prompt)
    glm_key = jp.GLM_KEY
    glm_model = jp.GLM_MODEL

    # sx_text = api.zhipu_chat(glm_key, glm_model, prompt)
    sx_text = api.generate_chat_completion(prompt)
    # 判断lm是不是数字, 如果不是则,lm为0
    return sx_text

# 处理字符串,不超过指定长度, 一个汉字当做两个字符, 超过的部分删除, 返回处理后的字符串
def handle_str_length(string, length):
    result = []
    count = 0

    for char in string:
        # 判断是否是中文字符
        if '\u4e00' <= char <= '\u9fff':
            count += 2
        else:
            count += 1

        if count > length:
            break
        result.append(char)

    return ''.join(result)

# 输入的s:68,m:79,l:81, 返回一个字典
def handle_sku_price_v2(sku_price):
    print(f"【sku价格格式化V2】入参={sku_price}")
    """
    输入的灰色:S:75,白色:XL:75, 返回一个二维数组
    :param sku_price:  输入的 灰色:S:75,白色:XL:75
    :return:  [['灰色','S','75'],['白色','XL','75']]
    """
    sku_price_format_array = []
    sku_price_list = sku_price.split(',')
    for sku in sku_price_list:
        sku = sku.split(':')
        sku_price_format_array.append(sku)
    print(f"【sku价格格式化V2】出参={sku_price_format_array}")
    return sku_price_format_array

# 输入的s:68,m:79,l:81, 返回一个字典
def handle_sku_price(sku_price):
    print(f"【sku价格格式化】入参={sku_price}")
    """
    输入的s:68,m:79,l:81, 返回一个字典
    :param sku_price:  输入的s:68,m:79,l:81
    :return:  返回一个字典
    """
    sku_price_dict = {}
    sku_price_list = sku_price.split(',')
    for sku in sku_price_list:
        sku = sku.split(':')
        sku_price_dict[sku[0]] = sku[1]
    print(f"【sku价格格式化】出参={sku_price_dict}")
    return sku_price_dict