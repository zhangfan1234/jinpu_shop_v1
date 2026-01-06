import os
import time
from time import sleep
from random import random, randint
from utils import api_requests as api
from click import clear
import utils.data_processing as data
from DrissionPage import ChromiumPage, ChromiumOptions
import pyperclip

# 淘宝上传图片
def tb_img_up(img_path_list, sp_tab):
    print(f"【淘宝发布商品】从本地上传img_path_list={img_path_list}")
    time.sleep(1)
    upload_img_path_list = img_path_list
    if len(upload_img_path_list) > 5:
        upload_img_path_list = upload_img_path_list[:5]
    sp_tab.ele("从本地上传").click.to_upload(upload_img_path_list[0])
    time.sleep(2)
    if len(upload_img_path_list) > 1:
        sp_tab.ele("从本地上传").click.to_upload(upload_img_path_list[1:])
    time.sleep(10)

    print(f"【淘宝发布商品】上传完成，确认，下一步")
    sp_tab.wait.eles_loaded("x://span[text()='确认，下一步']", timeout=12)
    sp_tab.ele("x://span[text()='确认，下一步']").click()


# 淘宝类目选择
def tb_category_input(sp_tab, goods_name, goods_desc, goods_brand, goods_id, goods_price, goods_sku_price, img_dir_path):
    print(f"【淘宝发布商品】类目选择goods_name={goods_name}, goods_desc={goods_desc}, goods_brand={goods_brand}, "
          f"goods_id={goods_id}, goods_price={goods_price}, goods_sku_price={goods_sku_price},"
          f" img_dir_path={img_dir_path}")
    print("【淘宝发布商品】点击更多类目")
    sp_tab.ele("更多类目").click()
    print(f"【淘宝发布商品】输入商品名称={goods_name}")
    sp_tab.ele("@placeholder:类目搜索：可输入产品名称").input(goods_name)
    print(f"【淘宝发布商品】点击搜索")
    sp_tab.ele("x://div[@role='dialog']//button/span[text()='搜索']").click()
    lm_eles = sp_tab.eles("x://ul[@role='menu']/li//span//span")  # 类目元素
    # 获取类目元素信息
    lm_texts = lm_eles.get.texts()
    print(f"【淘宝发布商品】获取类目元素信息={lm_texts}")
    # 调用AI获取类目序号
    try:
        print(f"【淘宝发布商品】调用AI获取类目序号goods_name={goods_name}, goods_desc={goods_desc}, "
              f"lm_texts={lm_texts}, img_dir_path={img_dir_path}")
        lm_index = data.get_ai_result_index(goods_name, goods_desc, lm_texts, img_dir_path)
        lm_name = lm_texts[lm_index]
        print(f"【淘宝发布商品】调用AI获取类目lm_name={lm_name}")
        lm_eles[lm_index].click()
    except:
        print(f"【淘宝发布商品】调用AI获取类目序号异常，默认序号0")
        lm_name = lm_texts[0]
        print(f"【淘宝发布商品】默认类目lm_name={lm_name}")
        lm_eles[0].click()
    sp_tab.ele("x://div[@role='dialog']//button/span[text()='确定']").click()
    try:
        sp_tab.ele("x://div[@role='alertdialog']//button/span[text()='确定']").click()
    except:
        pass
    time.sleep(1)

    # 如果存在特殊情况处理
    if sp_tab.wait.eles_loaded("x://div[@class='sell-component-item-prop ']//div[@role='gridcell']/div", timeout=1.5):
        print("【淘宝发布商品】存在特殊情况处理，进行淘宝属性填写")
        tb_attribute_input_1(sp_tab, goods_name, goods_desc, goods_brand, goods_id, goods_price, goods_sku_price, img_dir_path)
        print("【淘宝发布商品】特殊情况处理完成")
    time.sleep(1)
    # sp_tab.ele("x://div[@class='ai-category-image-footer']//button/span[text()='确认，下一步']").click()
    sp_tab.ele("x://button/span[text()='确认，下一步']").click()
    return lm_name

def tb_attribute_input_1(sp_tab,goods_name, goods_desc, goods_brand, goods_id, goods_price, goods_sku_price, img_dir_path):
    dict_m = {
        "编号": goods_id,
        "品牌": goods_brand,
        "标题": goods_name,
        "描述": goods_desc,
        "sku和价格": goods_price,
        "价格": goods_sku_price

    }
    print(f"【上传图页属性】属性编写dict_m={dict_m}")
    sleep(3)
    # img_page_attr_component_item = sp_tab.ele('.sell-component-item-prop ')
    # img_page_attr_eles = img_page_attr_component_item.eles('@role=gridcell')
    img_page_attr_eles = sp_tab.eles("x://div[@class='sell-component-item-prop ']//div[@role='gridcell']/div")
    print(f"【上传图页属性】属性节点长度={len(img_page_attr_eles)}")
    # input('这么刁钻吗？？？？？？？？？')
    for attribute_eles in img_page_attr_eles:
        attribute = attribute_eles.ele(".left-wrap")
        attribute_text = attribute.text  # 属性名称文本
        print(f"【上传图页属性】属性名称文本={attribute_text}")
        attribute_ele = attribute_eles.ele("x://div[@class='sell-itemProp-struct']/div[@class='content']")  # 属性交互元素
        print(f"【上传图页属性】attribute_text={attribute_text}")
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
            elif "年份季节" in attribute_text:
                attribute_eles.ele('@placeholder:请选择').click()
                attribute_eles.ele(".left-wrap").click()
                attribute_ele.click()
                time.sleep(1)
                shuxin_eles = sp_tab.eles("x://div[@class='options-content']//div[@class='options-item']")
                lm_index = 0
                shuxin_eles[lm_index].click()
                sleep(1)
                attribute.click()
                continue
            elif "性别" in attribute_text:
                attribute_eles.ele('@placeholder:请选择').click()
                attribute_eles.ele(".left-wrap").click()
                attribute_ele.click()
                time.sleep(1)
                shuxin_eles = sp_tab.eles("x://div[@class='options-content']//div[@class='options-item']")
                lm_index = 0
                shuxin_eles[lm_index].click()
                sleep(1)
                attribute.click()
                continue
            elif "服装版型" in attribute_text:
                attribute_eles.ele('@placeholder:请选择').click()
                attribute_eles.ele(".left-wrap").click()
                attribute_ele.click()
                time.sleep(1)
                shuxin_eles = sp_tab.eles("x://div[@class='options-content']//div[@class='options-item']")
                lm_index = 0
                shuxin_eles[lm_index].click()
                sleep(1)
                attribute.click()
                continue
            elif "面料织造方法" in attribute_text:
                attribute_eles.ele('@placeholder:请选择').click()
                attribute_eles.ele(".left-wrap").click()
                attribute_ele.click()
                time.sleep(1)
                shuxin_eles = sp_tab.eles("x://div[@class='options-content']//div[@class='options-item']")
                lm_index = 0
                shuxin_eles[lm_index].click()
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
                lm_index = data.get_ai_result_index(goods_name, goods_desc, shuxin_texts, img_dir_path)
                shuxin_eles[lm_index].click()
                sleep(1)
                attribute.click()
                continue

        elif "请输入" in attribute_ele.inner_html:
            if "市场价" in attribute_text:
                attribute_ele.ele("x://input").input("666", clear=True)
                sleep(1)
                attribute.click()
                continue
            shuru = data.get_ai_input(dict_m, attribute_text)

            attribute_ele.ele("x://input").input(shuru, clear=True)
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

# 淘宝商品属性填写
def tb_attribute_input_2(sp_tab,goods_name, goods_desc, goods_brand, goods_id, goods_price, goods_sku_price, img_dir_path):
    dict_m = {
        "编号": goods_id,
        "品牌": goods_brand,
        "标题": goods_name,
        "描述": goods_desc,
        "sku和价格": goods_price,
        "价格": goods_sku_price

    }
    print(f"【淘宝发布商品】属性编写dict_m={dict_m}")
    attribute_eles = sp_tab.eles("@id:sell-field-p-")
    print(f"【淘宝发布商品】属性节点attribute_eles={len(attribute_eles)}")
    for attribute_ele in attribute_eles:
        attribute_text = attribute_ele.text  # 属性名称文本
        print(f"【淘宝发布商品】attribute_text={attribute_text}")
        if "请选择" in attribute_ele.inner_html:
            if "年份季节" in attribute_text:
                attribute_ele.ele('@placeholder:请选择').click()
                time.sleep(1)
                shuxin_eles = sp_tab.eles("x://div[@class='options-content']//div[@class='options-item']")
                lm_index = 0
                shuxin_eles[lm_index].click()
                sleep(1)
                continue
            elif "性别" in attribute_text:
                attribute_ele.ele('@placeholder:请选择').click()
                time.sleep(1)
                shuxin_eles = sp_tab.eles("x://div[@class='options-content']//div[@class='options-item']")
                lm_index = 0
                shuxin_eles[lm_index].click()
                sleep(1)
                continue
            elif "服装版型" in attribute_text:
                attribute_ele.ele('@placeholder:请选择').click()
                time.sleep(1)
                shuxin_eles = sp_tab.eles("x://div[@class='options-content']//div[@class='options-item']")
                lm_index = 0
                shuxin_eles[lm_index].click()
                sleep(1)
                continue
            elif "面料织造方法" in attribute_text:
                attribute_ele.ele('@placeholder:请选择').click()
                time.sleep(1)
                shuxin_eles = sp_tab.eles("x://div[@class='options-content']//div[@class='options-item']")
                lm_index = 0
                shuxin_eles[lm_index].click()
                sleep(1)
                continue
            elif "适用人群" in attribute_text:
                attribute_ele.ele('@placeholder:请选择').click()
                time.sleep(1)
                shuxin_eles = sp_tab.eles("x://div[@class='options-content']//div[@class='options-item']")
                lm_index = 0
                shuxin_eles[lm_index].click()
                sleep(1)
                continue
        elif "请输入" in attribute_ele.inner_html:
            if "吊牌价" in attribute_text:
                attr_price_input_ele = attribute_ele.ele('tag=input')
                attr_price_input_ele.clear()
                time.sleep(1)
                attr_price_input_ele.input(dict_m.get('sku和价格'))
                sleep(1)
                continue
            if "品牌" in attribute_text:
                attr_price_input_ele = attribute_ele.ele('tag=input')
                attr_price_input_ele.clear()
                time.sleep(1)
                attr_price_input_ele.input(dict_m.get('品牌'))
                sleep(1)
                continue

# 销售属性与销售规格填写
def tb_spec_input(sp_tab, goods_sku_price, goods_stock, goods_price, sku_code, goods_id):
    print(f"【淘宝发布商品】淘宝规格填写goods_sku_price={goods_sku_price}, goods_stock={goods_stock}, "
          f"goods_price={goods_price}, sku_code={sku_code}, goods_id={goods_id}")
    sku_price_format_array = data.handle_sku_price_v2(goods_sku_price)
    stock_list = str(goods_stock).split(',')
    # 如果sku编码为空，就取商品编码
    sku_code_list = []
    if sku_code is None or len(sku_code) == 0:
        # 循环长度相同且非空的sku库存list
        for sku in stock_list:
            sku_code_list.append(goods_id)
    else:
        sku_code_list = str(sku_code).split(',')

    # 将数量集合、编码集合、颜色:尺码:价格集合  整合。他们长度相同
    goods_merge_attr = {}
    for idx, goods_stock in enumerate(stock_list):
        if goods_stock is None:
            continue
        goods_code = sku_code_list[idx]
        if goods_code is None:
            continue
        sku_info_arr = sku_price_format_array[idx]
        if sku_info_arr is None or len(sku_info_arr) == 0:
            continue
        goods_color = sku_info_arr[0]
        goods_size = sku_info_arr[1]
        goods_price = sku_info_arr[2]
        goods_merge_attr[f'{goods_color}-{goods_size}'] = [goods_color, goods_size, goods_price, goods_stock, goods_code]
        goods_merge_attr[f'{goods_size}-{goods_color}'] = [goods_color, goods_size, goods_price, goods_stock, goods_code]

    print(f"【淘宝发布商品】商品excel属性信息goods_merge_attr={goods_merge_attr}")

    # 删除销售属性信息
    sale_attr_ele = sp_tab.ele('@id=struct-saleProp')
    sale_attr_ele.eles('@id:struct-p-')

    # 删除多余的规格
    print("【淘宝发布商品】删除多余的规格")
    for i in range(len(sp_tab.eles("x://div[@class='next-loading-wrap']//li//button/i"))):
        print(f"【淘宝发布商品】删除多余的规格={i}")
        sp_tab.ele("x://div[@class='next-loading-wrap']//li[1]//button/i").click()

    # 添加规格
    print("【淘宝发布商品】添加规格")
    try:
        add_attr_record = []
        li_index = 1
        for sku_price_arr in sku_price_format_array:
            if len(sku_price_arr) == 0:
                continue
            goods_color = sku_price_arr[0]
            goods_size = sku_price_arr[1]
            # 属性名称-颜色,未添加过
            if goods_color not in add_attr_record:
                if li_index > 1:
                    sale_attr_ele = sp_tab.ele('@id=struct-saleProp')
                    sale_attr_ele.ele('.next-btn next-medium next-btn-normal add').click()
                print(f"【淘宝发布商品】添加商品属性-颜色={goods_color}")
                sp_tab.ele(
                    f'xpath://*[@id="struct-p-1627207"]/div/ul/div[{li_index}]/li/div[1]/div[2]/span/input').input(
                    goods_color, clear=True)
            if goods_size not in add_attr_record:
                if li_index > 1:
                    sale_attr_ele = sp_tab.ele('@id=struct-saleProp')
                    sale_attr_ele.ele('.next-btn next-medium next-btn-normal size-option-add-btn').click()
                print(f"【淘宝发布商品】添加商品属性-尺寸={goods_size}")
                # sp_tab.ele(f'xpath://*[@id="struct-p-20509"]/div[3]/div/div[2]/ul/li[{li_index}]/div[1]/div/div/span/input').input(goods_size, clear=True)
                sp_tab.ele(f'xpath://*[@id="struct-p-20509"]/div[2]/div/div[2]/ul/li[{li_index}]/div[1]/div/div/span/input').input(goods_size, clear=True)
            print(f"【淘宝发布商品】填完之后点一下，可能元素就不会消失了。")
            sp_tab.ele("x://span[@class='props-label' and text()='尺码']", timeout=3).click()
            time.sleep(1)
            # TODO: 获取页面规格属性信息，查询对应的属性配置行，如配置无，则跳过
            goods_arrt_tr_ele = sp_tab.ele(f"xpath://tr[@class='sku-table-row'][{li_index}]")
            row_idx = li_index
            while True:
                page_goods_color = goods_arrt_tr_ele.child(index=1).text
                page_goods_size = goods_arrt_tr_ele.child(index=2).text
                print(f'第{row_idx}行商品规格，颜色={page_goods_color}, 尺寸={page_goods_size}')
                # 判断当前规格是否在excel中，如果在则填写，不再则不填写，继续循环
                if f'{page_goods_color}-{page_goods_size}' in goods_merge_attr:
                    li_index = row_idx
                    break
                try:
                    goods_arrt_tr_ele = goods_arrt_tr_ele.next()
                except Exception as e:
                    goods_arrt_tr_ele = None
                if goods_arrt_tr_ele is None:
                    break
                row_idx += 1
            goods_key = f'{page_goods_color}-{page_goods_size}'
            goods_merge_list = goods_merge_attr.get(goods_key)
            goods_merge_color = goods_merge_list[0]
            goods_merge_size = goods_merge_list[1]
            goods_merge_price = goods_merge_list[2]
            goods_merge_stock = goods_merge_list[3]
            goods_merge_code = goods_merge_list[4]

            # 填写价格
            print(f"【淘宝发布商品】添加规格，填写价格={goods_merge_price}")
            price_ele = sp_tab.ele(f"x://tr[@class='sku-table-row'][{li_index}]/td[3]//input", timeout=5)
            price_ele.input(str(goods_merge_price), clear=True)
            # sp_tab.ele(f'x://*[@id="{li_index - 1}-skuPrice"]/div/div/span/span/span/input').input(value, clear=True)
            time.sleep(1)
            # 2次填写价格
            print(f"【淘宝发布商品】添加规格，填写价格={goods_merge_price}")
            price_ele = sp_tab.ele(f"x://tr[@class='sku-table-row'][{li_index}]/td[3]//input")
            price_ele.input(str(goods_merge_price), clear=True)
            # sp_tab.ele(f'x://*[@id="{li_index - 1}-skuPrice"]/div/div/span/span/span/input').input(value, clear=True)
            time.sleep(1)
            # 数量
            print(f"【淘宝发布商品】添加规格，填写数量={goods_merge_stock}")
            sp_tab.ele(f"x://tr[@class='sku-table-row'][{li_index}]/td[4]//input").input(goods_merge_stock, clear=True)
            time.sleep(2)
            # 商家编码
            print(f"【淘宝发布商品】添加规格，填写商家编码={goods_merge_code}")
            sp_tab.ele(f"x://tr[@class='sku-table-row'][{li_index}]/td[5]//input").input(goods_merge_code, clear=True)
            add_attr_record.append(goods_merge_color)
            add_attr_record.append(goods_merge_size)
            li_index += 1
    except Exception as e:
        print(f"sku异常,跳过sku, 改为一口价。 异常信息: {e}")
        sp_tab.ele("x://div[@id='struct-price']//input").input(goods_price, clear=True)


# 淘宝详情处理
def tb_detail_handle(sp_tab, goods_desc, img_path_list):
    print('淘宝详情处理')
    try:
        # 删除默认的图片模板
        if sp_tab.wait.eles_loaded('#panel_edit', timeout=2):
            img_ele = sp_tab.ele('#panel_edit')
            print('点击删除默认的图片模板')
            del_img_eles = img_ele.eles('@data-type=delete')
            for img_ele in del_img_eles:
                img_ele.click()
        print('点击元素dragStream--Sa6Kj')
        sp_tab.ele('x://*[@id="panel_edit"]/div[2]/div[2]/div/div/div[2]/div/div').click()
        print('点击元素dragStream--dialog')
        sp_tab.ele("x://div[@role='dialog']//button[1]").click()
    except:
        print('淘宝详情处理-点击元素未知异常，忽略')
        pass
    # 添加文字
    print('淘宝详情处理-添加文字')
    sp_tab.ele('@@class:add_item_name-@@text():文字').click()
    # sp_tab.ele(".editor--GiZhF").ele("文字").click()
    print('淘宝详情处理-点击dragStream--Sa6Kj')
    # txt_ele = sp_tab.ele("x://div[@class='dragStream--Sa6Kj']/div[1]").click()
    print(f'淘宝详情处理-输入详情描述信息={goods_desc}')
    sp_tab.ele("@placeholder:文本模块,此处可以输入商品详情的描述信息").input(goods_desc)
    print(f'淘宝详情处理-添加图片')
    # 添加图片
    # sp_tab.ele(".editor--GiZhF").ele("图片").click()
    sp_tab.ele('@@class:add_item_name-@@text():图片').click()
    print(f'淘宝详情处理-等待选择图片加载')
    if sp_tab.wait.eles_loaded("选择图片", timeout=10):
        # shunxu_dict = {}
        index_s = 0
        # 图片排序
        print(f'淘宝详情处理-图片排序')
        # for index_ele in sp_tab.eles("x://div[@id='sucai_tu_selector_scrollMain']/div//span[contains(text(), 'jpg')]")[:good_len]:
        #     index = index_ele.text.split(".")[0]
        #     shunxu_dict.setdefault(int(index), index_s)
        #     index_s += 1
        #     print(f'淘宝详情处理-index_s={index_s}')

        # 按顺序点击
        try:
            good_len = len(img_path_list)
            print(f'淘宝详情处理-按顺序点击good_len={good_len}')
            img_eles = sp_tab.eles("@class:PicList_pic_background_")
            for img_path in img_path_list:
                file_name_str = os.path.basename(img_path)
                for img_ele in img_eles:
                    # 获取文本、判断当前元素中是否在，存在则点击
                    cloud_img_text = img_ele.text
                    print(f'获取云空间图片名称={cloud_img_text}')
                    if file_name_str in cloud_img_text:
                        print(f'点击选中={file_name_str}')
                        img_ele.ele('.next-checkbox-input').click(by_js=True)
                        break

        except:
            print(f'淘宝详情处理-出现未知异常')
            pass

        # 确定按钮
        print(f'淘宝详情处理-点击 确定')
        sp_tab.ele("确定（").click()


# ai自动判断闲鱼分类
def xy_category_ai(goods_name, goods_desc):
    # 提示词
    prompt = f"""
        商品标题: {goods_name}
        详情描述: {goods_desc}
    """

    # 初始化浏览器
    co = ChromiumOptions().set_paths(local_port=9999)
    page = ChromiumPage(addr_or_opts=co)
    glm_tab = page.new_tab("https://open.bigmodel.cn/shareapp/v1/?share_code=fIZC7YpD2sBQvk0OVd15c")

    # 输入问题并点击
    glm_tab.ele("x://div//textarea").input(prompt)
    if glm_tab.ele("x://div[@class='el-tooltip']").wait.enabled():
        glm_tab.ele("x://div[@class='el-tooltip']").click()

    # 等待回复复制内容
    if glm_tab.wait.eles_loaded("tag:i@@class=el-tooltip iconfont button icon-wdfuzhi1 absolute right-0 md:relative", timeout=10):
        glm_tab.ele("tag:i@@class=el-tooltip iconfont button icon-wdfuzhi1 absolute right-0 md:relative").click()
    fl_text = pyperclip.paste()
    fl_text = fl_text.replace("潮品 / 其他男鞋 / 其他男鞋 / 其他男鞋：", "")
    glm_tab.close()
    return fl_text


# 闲鱼商品属性填写
def xy_attribute_input(sp_tab,goods_name, goods_desc, goods_brand, goods_stock):
    if sp_tab.wait.eles_loaded("商品属性", timeout=10):
        stock_list = str(goods_stock).split(',')
        # 品牌填写
        if sp_tab.wait.eles_loaded(f"x://div[@class='radio-label' and text()=' {goods_brand} ']", timeout=1):
            sp_tab.ele(f"x://div[@class='radio-label' and text()=' {goods_brand} ']").click()
        elif sp_tab.wait.eles_loaded("x: //span[text()=' 添加 ']", timeout=1):
            sp_tab.ele("x://input[@placeholder='请输入品牌']").input(goods_brand)
            sp_tab.ele("x: //span[text()=' 添加 ']").click()
        else:
            #搜索品牌
            search_list = [goods_brand,"other/其他", "其他", "其她", "其它", "qita", "other"]
            find_one_brand = False
            for i in range(len(search_list)):
                search_goods_brand = search_list[i]
                sp_tab.ele(
                    f'x://form//div[contains(@class, "first-radio")]//div[contains(@class, "el-input--prefix")]/input[@type="text"]',
                    timeout=5).input(search_goods_brand,clear=True)
                brand_li_path = 'x://div[contains(@class,"el-autocomplete-suggestion")]//ul/li'
                find_brand = False
                if sp_tab.wait.eles_loaded(brand_li_path,timeout=5):
                   brands = sp_tab.eles(brand_li_path)
                   if len(brands) > 0:
                       for i in range(len(brands)):
                           text = brands[i].text
                           if text.lower() == search_goods_brand.lower():
                               print(f"搜索品牌:{search_goods_brand}成功")
                               brands[i].click()
                               find_brand = True
                if find_brand:
                    find_one_brand = True
                    break
            if not find_one_brand:
                print(f'未搜索到品牌:{goods_brand}和其他品牌')
                # raise  f'未搜索到品牌:{goods_brand}和其他品牌'
        # 其他属性处理
        for ele in sp_tab.eles("x://div[@class='el-form-item radio-item']"):
            # 获取标题和选项元素
            title = ele.ele("x:/label/span").text
            sx_eles = ele.eles("x:/div/div[@class='radio-label']")
            sx_texts = sx_eles.get.texts()

            if title == "尺码":
                if len(stock_list) > 1:
                    if "均码" in sx_texts:
                        sp_tab.ele(f"x://div[@class='radio-label' and text()=' 均码 ']").click()
                        continue

            if title == "成色":
                sx_eles[0].click()
                continue
            else:
                sx_index = data.get_ai_result_index_xy(goods_name, goods_desc, sx_texts)
                sx_eles[sx_index].click()


# 闲鱼图片上传
def xy_img_up(img_path_list, sp_tab):
    sp_tab.ele("上传图片").click.to_upload(img_path_list[0])
    time.sleep(1)
    sp_tab.ele("上传图片").click.to_upload(img_path_list[1:])
    time.sleep(1)
# 多sku输入标签值
def xy_input_label_value(sp_tab,label,value):
    sp_tab.ele(f"x://input[@placeholder='请输入{label}名称，按“回车键”确认']", timeout=2).input(value, clear=True)
    sp_tab.ele('x://button/span[normalize-space(.)="添加"]', timeout=2).click()
def xy_select_region(sp_tab,province,city,district):
    '''

    Args:
        sp_tab: 页面
        province: 省
        city: 市
        district:区

    Returns:

    '''
    sp_tab.ele('x://form//form//div[@class="el-form-item__content"]//div[contains(@class, "el-select")]',timeout=5).click()
    sp_tab.ele('x://form//input[contains(@class, "el-input")][@placeholder="省"]',timeout=5).click()
    sp_tab.ele(f'x://ul/li[normalize-space(.)="{province}"]',timeout=5).click()
    sp_tab.ele('x://form//input[contains(@class, "el-input")][@placeholder="市"]',timeout=5).click()
    sp_tab.ele(f'x://ul/li[normalize-space(.)="{city}"]',timeout=5).click()
    sp_tab.ele('x://form//input[contains(@class, "el-input")][@placeholder="区"]', timeout=5).click()
    sp_tab.ele(f'x://ul/li[normalize-space(.)="{district}"]',timeout=5).click()
    sp_tab.ele('x://button/span[normalize-space(.)="确认选择"]',timeout=5).click()
#咸鱼多sku根据颜色，尺码输入价格，库存，编码
def xy_input_sku_data(web,color, size, price, stock, code):
    """
     在表格中根据颜色和尺码输入SKU数据

     参数:
     web: ChromiumPage或ChromiumTab对象
     color: 颜色字符串
     size: 尺码字符串
     price: 价格字符串或数字
     stock: 库存字符串或数字
     code: 商家编码字符串
     """
    try:
        # 等待表格加载
        body = web.ele('.el-table__body tbody', timeout=5)

        # 获取所有行
        rows = web.eles('.el-table__row')

        # 遍历每一行，查找匹配的颜色和尺码
        target_row = None
        for row in rows:
            # 获取颜色和尺码单元格
            color_cell =row.ele('xpath:.//td[2]', timeout=2)
            size_cell = row.ele('xpath:.//td[3]', timeout=2)

            if color_cell and size_cell:
                cell_color = color_cell.text.strip()
                cell_size = size_cell.text.strip()

                # 如果匹配到指定的颜色和尺码
                if cell_color == color and cell_size == size:
                    target_row = row
                    break

        if not target_row:
            print(f"未找到颜色为'{color}'，尺码为'{size}'的行")
            return False

        print(f"找到匹配行: 颜色={color}, 尺码={size}")

        # 输入价格
        price_cell = target_row.ele('xpath:.//td[4]', timeout=2)

        if price_cell and price:
            # 查找编辑按钮并点击
            price_cell.hover()
            time.sleep(0.5)
            edit_btn = price_cell.ele('x://span[contains(@class, "bjbtn")]', timeout=2)
            if edit_btn:
                edit_btn.click()
                # 查找输入框并输入价格
                price_input = price_cell.ele('x://input[@class="el-input__inner"]', timeout=2)
                if price_input:
                    price_input.input(str(price))
                    # 点击其他地方使输入框失焦（保存）
                    price_cell.click()
                    print(f"已输入价格: {price}")

        # 输入库存
        stock_cell = target_row.ele('xpath:.//td[5]', timeout=2)
        if stock_cell and stock:
            # 查找编辑按钮并点击
            stock_cell.hover()
            time.sleep(0.5)
            edit_btn = stock_cell.ele('x://span[contains(@class, "bjbtn")]', timeout=2)
            if edit_btn:
                edit_btn.click()


                # 查找输入框并输入库存
                stock_input = stock_cell.ele('x://input[@class="el-input__inner"]', timeout=2)
                if stock_input:
                    stock_input.input(str(stock))


                    # 点击其他地方使输入框失焦（保存）
                    stock_cell.click()

                    print(f"已输入库存: {stock}")

        # 输入商家编码
        code_cell =  target_row.ele('xpath:.//td[6]', timeout=2)
        if code_cell and code:
            # 查找编辑按钮并点击
            code_cell.hover()
            time.sleep(0.5)
            edit_btn = code_cell.ele('x://span[contains(@class, "bjbtn")]', timeout=2)
            if edit_btn:
                edit_btn.click()


                # 查找输入框并输入商家编码
                code_input = code_cell.ele('x://input[@class="el-input__inner"]', timeout=2)
                if code_input:
                    code_input.input(str(code))


                    # 点击其他地方使输入框失焦（保存）
                    code_cell.click()

                    print(f"已输入商家编码: {code}")

        print("SKU数据输入完成")
        return True

    except Exception as e:
        print(f"输入SKU数据时发生错误: {str(e)}")
        return False
# 微店图片上传
def wd_img_up(img_path_list, sp_tab):
    sp_tab.ele("x://div[@class='draggable-item']").click()
    sp_tab.ele("x://div[@class='img-content']//button").click()
    time.sleep(1)
    sp_tab.ele("x://div[@class='el-dialog__body']//i[@class='el-icon-plus']").click.to_upload(img_path_list[0])
    time.sleep(1)
    sp_tab.ele("x://div[@class='el-dialog__body']//i[@class='el-icon-plus']").click.to_upload(img_path_list[1:])
    time.sleep(1)
    sp_tab.ele("x:(//div[@class='el-dialog']//button[@data-spider-action-name='img-submit-upload'])[1]").click()

    # 等待上传图标消失
    print('等待上传图标消失')
    if sp_tab.wait.ele_deleted("x://div[@class='el-loading-spinner']", timeout=20):
        pass


# 微店类目选择
def wd_category_input(sp_tab, goods_name, goods_desc, img_path_t):

    sp_tab.ele("x://button/span[text()='选择商品类目']").click(by_js=True)
    goods_name_enter = f"{goods_name}\n"
    sp_tab.ele("x://div[@class='category-search']//input").input(goods_name_enter, clear=True)
    time.sleep(1)
    lm_text = ""
    try:
        lm_eles = sp_tab.eles("x:(//div[@class='el-select-dropdown el-popper'])[12]//li")[:5]
        lm_texts = []
        for le_ele in lm_eles:
            lm_texts.append(le_ele.text)
        index = data.get_ai_result_index(goods_name, goods_desc, lm_texts, img_path_t) + 1
        x_path = "x:(//div[@class='el-select-dropdown el-popper'])[12]//li[" + str(index) + "]"
        sp_tab.ele(x_path, timeout=3).click()
        lm_text = sp_tab.ele(x_path, timeout=3).ele("x:/div").text
    except:
        pass

    sp_tab.ele("x://div[@aria-label='选择商品类目']//button/span[text()='确定']", timeout=3).click()
    return lm_text


# 微店商品详情
def wd_detail_handle(sp_tab, goods_desc):
    time.sleep(1)
    sp_tab.ele("自动生成商品详情").click()
    sleep(1)
    sp_tab.ele("x://div[@class='show__text']").click()
    sleep(1)
    sp_tab.ele("x://div[@data-ph='请输入内容']").input(goods_desc)

#微店多sku输入
def wd_input_sku_data(sp_tab,color, size, price, stock, code):
    """
    根据颜色和尺码在表格中的位置输入数据
    """
    # 找到所有颜色行（具有rowspan属性的行）
    color_rows = sp_tab.eles('xpath://tbody/tr/td[@rowspan and contains(@class, "td__text__top")]/..')

    for color_row in color_rows:
        # 获取颜色文本
        color_div = color_row.ele('xpath:.//div[@class="multi-sku-table__sku-name"]/div')
        color_div.scroll.to_center()
        current_color = color_div.text.strip() if color_div else ""

        # 跳过表头行：如果颜色文本为空或者是表头列名
        if not current_color or current_color in ["颜色", "尺码", "价格", "库存", "编码"]:
            continue

        if current_color == color:
            # 获取该颜色下的所有尺码行
            # rowspan值表示该颜色跨多少行
            rowspan = int(color_row.ele('xpath:.//td[@rowspan]').attr('rowspan') or 1)

            # 获取从当前行开始的连续rowspan行
            for i in range(rowspan):
                row_index = color_rows.index(color_row) + i
                all_rows = sp_tab.eles('xpath://tbody/tr')
                if row_index < len(all_rows):
                    row = all_rows[row_index]

                    # 获取尺码
                    size_div = row.ele(
                        'xpath:.//div[@class="multi-sku-table__sku-name"]/div[not(contains(text(), "{}"))]'.format(
                            color), timeout=1)
                    current_size = size_div.text.strip() if size_div else ""

                    if current_size == size:
                        # 找到价格列（第9个td，索引从1开始）
                        price_td = row.ele('xpath:.//td[5]', timeout=2)
                        if price_td:
                            price_div = price_td.ele('xpath:.//div[contains(@class, "item-edit__input__fake")]',
                                                     timeout=1)
                            if price_div:
                                price_div.click()
                                time.sleep(0.5)
                                # 查找激活的输入框
                                active_input = row.ele(
                                    'xpath://input[@type="number" and contains(@class, "el-input__inner") and @placeholder=""]',
                                    timeout=1)
                                if active_input:
                                    active_input.input(price)

                        # 找到库存列（第11个td）
                        stock_td = row.ele('xpath:.//td[6]', timeout=2)
                        if stock_td:
                            stock_div = stock_td.ele('xpath:.//div[contains(@class, "item-edit__input__fake")]',
                                                     timeout=1)
                            if stock_div:
                                stock_div.click()
                                time.sleep(0.5)
                                active_input = row.ele(
                                    'xpath://input[@type="number" and contains(@class, "el-input__inner") and @input-int="true"]',
                                    timeout=1)
                                if active_input:
                                    active_input.input(stock)

                        # 找到编码列（第13个td）
                        code_td = row.ele('xpath:.//td[9]', timeout=2)
                        if code_td:
                            code_div = code_td.ele('xpath:.//div[contains(@class, "item-edit__input__fake")]',
                                                   timeout=1)
                            if code_div:
                                code_div.click()
                                time.sleep(0.5)
                                # 尝试查找textarea
                                textarea = code_td.ele('xpath://textarea[contains(@class, "el-textarea__inner")]', timeout=1)
                                if textarea:
                                    textarea.input(code)
                        return True

    print(f"未找到颜色 '{color}' 尺码 '{size}' 的行")
    return False

# 淘宝循环点击上传1：1主图
def tb_pust_zt(sp_tab, len_list):
    sp_tab.ele("x:(//div[@id='struct-mainImagesGroup']//div[text()='上传图片'])[1]").click()
    if sp_tab.wait.eles_loaded("选择图片", timeout=10):
        shunxu_dict = {}
        index_s = 0
        # 图片排序
        for index_ele in sp_tab.eles(
                "x://div[@id='sucai_tu_selector_scrollMain']/div//span[contains(text(), 'jpg')]")[:len_list]:
            index = index_ele.text.split(".")[0]
            shunxu_dict.setdefault(int(index), index_s)
            index_s += 1

        # 按顺序点击
        try:
            key_index = 1
            for i in range(len_list):
                index = shunxu_dict[key_index]
                sp_tab.eles("x://div[@id='sucai_tu_selector_scrollMain']/div//span[@class='next-checkbox']")[
                    index].click(
                    by_js=True)
                if key_index == 5:
                    break
                key_index += 1
        except:
            pass