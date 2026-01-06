from time import sleep

from DrissionPage import ChromiumPage, ChromiumOptions
from click import clear

import utils.web_automation as web
import time
from random import randint
import utils.data_processing as data

co = ChromiumOptions().set_paths(local_port=9999)
page = ChromiumPage(addr_or_opts=co)
goods_name = "azul by moussy日单女款短袖落肩纯棉华夫格白色休闲孤品重磅高克重圆领T恤"
goods_desc = """azul by moussy日单女款短袖落肩纯棉华夫格白色休闲孤品重磅高克重圆领T恤
e4j7l18e01
尺码m 肩宽5 胸围10 衣长6 袖长5
尺码l 肩宽6 胸围12 衣长7 袖长11
"""
goods_id = "e4s9p1801"
goods_brand = "azul by moussy"
goods_sku_price = "m:68,s:30,xl:50,xxl:60"
goods_stock = "1,5,8,10"
goods_price = "99"
sp_tab = page.get_tab(title="商品发布")
# xy_fl_tab = page.get_tab(title="分类机器人")
# xy_tab = page.get_tab(title="新建商品")
# wd_tab = page.get_tab(title="微店")
# 浏览器初始化

# page.new_tab("https://loginmyseller.taobao.com/")

# # 选择类目
# web.tb_category_input(sp_tab, goods_name, goods_desc, goods_brand)
#
# # # 填写标题
# goods_name = data.handle_str_length(goods_name, 59)
# sp_tab.ele("x://div[@id='struct-title']//input").input(goods_name)  # 商品标题

# # 类目属性
# web.tb_attribute_input(sp_tab, goods_name, goods_desc, goods_brand)

# # 淘宝规格填写
# web.tb_spec_input(sp_tab, goods_sku_price, goods_stock)

# sp_tab.ele("24小时内发货").click()


# 详情描述
# 删除默认的图片模板

# 闲鱼ai判断分类
# print(web.xy_category_ai(goods_name, goods_desc))

# 属性填写
# web.xy_attribute_input(xy_tab,goods_name, goods_desc, goods_brand)

# 闲鱼门店填写

# 等待图片上传消失
# if wd_tab.wait.ele_deleted("x://div[@class='el-loading-spinner']", timeout=20):
#     print("消失")
# else:
#     print("没消失")

# 微店分类选择
# web.wd_category_input(wd_tab, goods_name)


# 微店点击分类
# wd_tab.ele("x://button/span[text()='选择商品类目']").click(by_js=True)

# 微店价格库存
# wd_tab.ele("x://input[@placeholder='请填写商品价格']").input(goods_price, clear=True)
# stock_list = str(goods_stock).split(',')
# stock = sum([int(i) for i in stock_list])
# wd_tab.ele("x://input[@placeholder='请填写商品库存']").input(stock, clear=True)

# 微店下一步
# wd_tab.ele("下一步").click()

# 获取微店选择 类目
# lm = wd_tab.ele("x:(//div[@class='el-select-dropdown el-popper'])[12]//li[1]", timeout=3).ele("x:/div").text
# print(lm)


# # 淘宝详情图片
# len1 = 6
# shunxu_dict = {}
# index_s = 0
#
# for index_ele in sp_tab.eles("x://div[@id='sucai_tu_selector_scrollMain']/div//span[contains(text(), 'jpg')]")[:len1]:
#     index = index_ele.text.split(".")[0]
#     shunxu_dict.setdefault(int(index), index_s)
#     index_s += 1
#
# key_index = 1
# for i in range(len1):
#     index = shunxu_dict[key_index]
#     print(index)
#     sp_tab.eles("x://div[@id='sucai_tu_selector_scrollMain']/div//span[@class='next-checkbox']")[index].click(by_js=True)
#     key_index += 1


# sp_tab.ele("x://div[@class='options-search']/span/input").input("", clear=True)
# time.sleep(1)
# # 随机点击品牌
# num = randint(1, 5)
# xpath = f"x://div[@class='options-item'][{num}]"
# sp_tab.ele(xpath).click()



sleep(2)
sp_tab.ele("x:(//div[@id='struct-mainImagesGroup']//div[text()='上传图片'])[1]").click()
if sp_tab.wait.eles_loaded("选择图片", timeout=10):
    shunxu_dict = {}
    index_s = 0
    # 图片排序
    for index_ele in sp_tab.eles(
            "x://div[@id='sucai_tu_selector_scrollMain']/div//span[contains(text(), 'jpg')]")[:7]:
        index = index_ele.text.split(".")[0]
        shunxu_dict.setdefault(int(index), index_s)
        index_s += 1

    # 按顺序点击
    index = shunxu_dict[1]
    sp_tab.eles("x://div[@id='sucai_tu_selector_scrollMain']/div//span[@class='next-checkbox']")[index].click(by_js=True)

    # 确定按钮
    sleep(2)
    sp_tab.ele("确定（").click()


# 淘宝新属性
def tb_sx():
    dict_m = {
        "编号" : "e4s9p1801",
        "品牌" : "azul by moussy",
        "标题" :"azul by moussy日单女款短袖落肩纯棉华夫格白色休闲孤品重磅高克重圆领T恤",
        "描述" : """azul by moussy日单女款短袖落肩纯棉华夫格白色休闲孤品重磅高克重圆领T恤
e4j7l18e01
尺码m 肩宽5 胸围10 衣长6 袖长5
尺码l 肩宽6 胸围12 衣长7 袖长11
""",
        "sku和价格" : "m:68,s:30,xl:50,xxl:60",
        "价格" : "99"
    }
    attribute_eles = sp_tab.eles("x://div[@class='sell-component-item-prop ']//div[@role='gridcell']/div")
    for attribute_eles in attribute_eles:
        attribute =  attribute_eles.ele(".left-wrap")
        attribute_text = attribute.text  # 属性名称文本
        attribute_ele = attribute_eles.ele("x://div[@class='sell-itemProp-struct']/div[@class='content']")  # 属性交互元素

        if "请选择" in attribute_ele.inner_html:
            if attribute_text == "品牌":
                attribute_eles.ele(".left-wrap").click()
                attribute_ele.click()
                sp_tab.ele("x://div[@class='options-search']/span/input").input(goods_brand)
                time.sleep(1)
                if sp_tab.wait.eles_loaded("无选项", timeout=2):
                    sp_tab.ele("x://div[@class='options-search']/span/input").input("",clear=True)
                    sleep(1)
                    num = randint(1, 5)
                    xpath = f"x://div[@class='options-item'][{num}]"
                    sp_tab.ele(xpath).click()
                else:
                    sp_tab.ele(".options-item").click()
                sleep(1)
                attribute.click()
                continue
            elif attribute_text == "材质成分":
                # 其他 100%
                sp_tab.ele("添加材质成分").click()
                sp_tab.ele(".material-item").ele("@placeholder:请选择材质").click()
                sp_tab.ele("x://div[@class='options-search']/span/input").input("其他材质")
                time.sleep(1)
                sp_tab.ele(".options-item").click()
                # 如果 输入含量存在
                wait_bool = sp_tab.wait.eles_loaded("@placeholder:输入含量", timeout=1.5)
                if wait_bool:
                    sp_tab.ele("@placeholder:输入含量").input("100")
                sleep(1)
                attribute.click()
                continue
            else:
                # 其他属性
                attribute_eles.ele(".left-wrap").click()
                attribute_ele.click()
                time.sleep(1)
                shuxin_eles = sp_tab.eles("x://div[@class='options-content']//div[@class='options-item']")
                shuxin_texts = shuxin_eles.get.texts()
                lm_index = data.get_ai_result_index(goods_name, goods_desc, shuxin_texts)
                shuxin_eles[lm_index].click()
                sleep(1)
                attribute.click()
                continue

        elif "请输入" in attribute_ele.inner_html:
            shuru = data.get_ai_input(dict_m, attribute_text)
            print(shuru)
            attribute_ele.ele("x://input").input(shuru, clear=True)
            sleep(1)
            attribute.click()
