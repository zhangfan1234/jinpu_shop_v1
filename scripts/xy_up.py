# -*- coding: utf-8 -*-
'''
@Time    : 2025-11-16 09:46
@Author  : AnTi
@File    : test.py
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple ccxt
'''
import os.path
import time
from DrissionPage import ChromiumPage, ChromiumOptions
import utils.web_automation as web
import utils.file_operations as file
import utils.excel_operations as excel
import utils.api_requests as ai


def xy_main(xy_dict_list,excel_path,image_path):
    print(f"==================== 闲鱼开始上传 共{len(xy_dict_list)}个 ====================")

    # 打开浏览器到闲鱼, 进入到商品发布页
    co = ChromiumOptions().set_paths(local_port=9999)
    co.set_argument('--disable-features=BlockInsecurePrivateNetworkRequests')
    page = ChromiumPage(addr_or_opts=co)

    # in_sp_tab = page.new_tab("https://goofish.pro/sale/product/all")

    for xy_dict in xy_dict_list:
        # 新建商品页
        in_sp_tab = page.new_tab("https://goofish.pro/sale/product/all")
        # in_sp_tab = page.new_tab("https://goofish.pro/sale/product/add?from=/all")
        if in_sp_tab.wait.eles_loaded("x://button/span[text()='新建商品']"):
            in_sp_tab.ele("x://button/span[text()='新建商品']").click()
            xy_shop_up(in_sp_tab, xy_dict, excel_path, image_path)
            print(xy_dict['id'], "发布成功")


# 闲鱼单商品上传流程
def xy_shop_up(in_sp_tab, xy_dict,excel_path,image_path):

    # 提取数据
    goods_id = xy_dict['id'].strip()
    goods_name = xy_dict['name']
    goods_desc = xy_dict['desc']
    goods_brand = xy_dict['brand']
    goods_sku_price = xy_dict['sku_price']
    goods_price = xy_dict['price']
    goods_stock = xy_dict['stock']
    sku_code = xy_dict['sku_code']
    xy_mendian = xy_dict['xy_mendian']

    print(f'goods_sku_price={goods_sku_price}')
    print(f'goods_sku_price type={type(goods_sku_price)}')
    # 点击 普通商品
    in_sp_tab.wait.eles_loaded("text:普通商品", timeout=3)
    time.sleep(2)
    in_sp_tab.ele(f"text:普通商品").click()

    # ai自动判断闲鱼分类
    # fl_text = web.xy_category_ai(goods_name, goods_desc)
    try_sel_category_count = 0
    try_msg = ''
    while try_sel_category_count < 3:
        try_sel_category_count += 1
        # 修改为通义千问
        fl_text = ai.generate_category(
            f'{goods_desc} 帮我匹配一条合适的类目{try_msg}，不要有其他过多的说明，只需告诉我类目即可')
        try:
            in_sp_tab.ele("x://input[@placeholder='请输入关键词']").input(fl_text)
            time.sleep(1)
            if in_sp_tab.wait.eles_loaded(f"text:{fl_text}",timeout=5):
                in_sp_tab.ele(f"text:{fl_text}").click()
            else:
                fl_texts = fl_text.split("/")
                fl_text = fl_texts[len(fl_texts) - 1]
                print('未搜索到全路径类目，开始搜索最后类目项:'+fl_text)
                in_sp_tab.ele("x://input[@placeholder='请输入关键词']").input(fl_text,clear=True)
                print(f'当前类目[{fl_text}]未加载，更换类目尝试。')
                time.sleep(1)
                if  in_sp_tab.wait.eles_loaded('x://form//div[contains(@class, "custom-cascader__suggestion-item")]',timeout=3):
                    items = in_sp_tab.eles('x://form//div[contains(@class, "custom-cascader__suggestion-item")]')
                    items[0].click()
                else:
                    raise f'类目未找到'+fl_text
            break
        except:
            if len(try_msg) == 0:
                try_msg += f'，不能包含:[{fl_text}]'
            else:
                try_msg += f'[{fl_text}]'

    # 闲鱼属性填写
    # web.xy_attribute_input(in_sp_tab, goods_name, goods_desc, goods_brand, goods_stock)
    # 闲鱼门店选择
    print(f'【闲鱼门店选择】{xy_mendian}')
    # 判断当前店铺是否选中状态
    print(f'店铺选中状态={in_sp_tab.ele(f"text:{xy_mendian}").parent("tag=li").attr("class")}')

    if 'selected' != in_sp_tab.ele(f"text:{xy_mendian}").parent('tag=li').attr('class'):
        in_sp_tab.ele(f"text:{xy_mendian}").click()



    # 商品信息填写
    if in_sp_tab.wait.eles_loaded("商品信息", timeout=10):
        spxx = in_sp_tab.ele('x://form//div[normalize-space(.)="商品信息"]')
        spxx.scroll.to_center()
        # 商品信息填写 -- 图片上传

        img_dir_path = os.path.join(image_path,goods_id)   # 商品主图路径
        img_path_list = file.get_filepath_from_dir(img_dir_path, 'jpg')  # 获取商品主图路径下的所有jpg文件路径列表

        print(f'【商品图片上传】img_path_list={img_path_list}')
        web.xy_img_up(img_path_list, in_sp_tab)
        in_sp_tab.wait.doc_loaded()
        # 商品信息填写 -- 标题描述
        # goods_name = data.handle_str_length(goods_name, 29) # 截取标题长度
        print(f'【输入商品标题】goods_name={goods_name}')

        input_ele = in_sp_tab.ele("x://input[contains(@placeholder, '请输入商品标题')]",timeout=60)

        input_ele.input(goods_name)  # 商品标题
        print(f'【输入商品描述】goods_desc={goods_desc}')
        in_sp_tab.ele("x://textarea[contains(@placeholder,'请输入商品描述')]",timeout=4).input(goods_desc)  # 商品描述


    # 发货地区
    print('输入发货区域：天津-天津市-河东区')
    web.xy_select_region(in_sp_tab,'天津','天津市','河东区')

    stock_list = str(goods_stock).split(',')
    goods_sku_price_list = goods_sku_price.split(',')
    sku_list = sku_code.split(',')
    if len(goods_sku_price_list) > 1 and len(stock_list) == len(goods_sku_price_list) and len(sku_list) == len(stock_list) :
        # '//form//span[normalize-space(.)="添加多规格深库存"]'
        print('多sku上传')
        mutil_spec_radio = in_sp_tab.ele("添加多规格深库存",timeout=1)
        mutil_spec_radio.scroll.to_center()
        time.sleep(0.5)
        mutil_spec_radio.click()

        color_list = []
        size_list = []
        color_size_dic = {}
        default_price = 0
        for i in range(len(goods_sku_price_list)):
            color_size_price_tuple = goods_sku_price_list[i].split(":")
            color = color_size_price_tuple[0]
            size = color_size_price_tuple[1]
            price = color_size_price_tuple[2]
            if price is None or len(price) ==0:
                price = default_price
            default_price = price
            if color not in color_list:
                color_list.append(color)
            if size not in size_list:
                size_list.append(size)
            key = f'{color}-{size}'
            color_size_dic[key] = {
                'price':price,
                'stock':stock_list[i],
                'sku':sku_list[i]
            }

        in_sp_tab.ele('x://ul/li[normalize-space(.)="颜色"]',timeout=4).click()
        in_sp_tab.ele('x://button/span[normalize-space(.)="添加"]', timeout=2).click()

        if len(color_list) == 1:
            '''咸鱼至少2种颜色，使用默认色'''
            color_list.append('默认色')
        if len(size_list) == 1:
            '''咸鱼至少2种尺码，使用均码'''
            size_list.append('均码')
        for i  in range(len(color_list)):
            in_sp_tab.ele(f"x://input[@placeholder='请输入颜色名称，按“回车键”确认']", timeout=2).input(color_list[i], clear=True)
            in_sp_tab.ele('x://button/span[normalize-space(.)="添加"]', timeout=2).click()

        in_sp_tab.ele('x://div[@class="more-wrape"]/div[normalize-space(.)="添加商品规格"]',timeout=2).click()
        in_sp_tab.ele('x://ul/li[normalize-space(.)="尺码"]',timeout=4).click()
        in_sp_tab.ele('x://div[@class="first-add-wrape"]/button[normalize-space(.)="添加"]', timeout=2).click()
        for i  in range(len(size_list)):
            in_sp_tab.ele(f"x://input[@placeholder='请输入尺码名称，按“回车键”确认']", timeout=2).input(size_list[i], clear=True)
            in_sp_tab.ele('x://div[@class="info-values last"]//button[span="添加"]',timeout=4).click()
        #完成添加
        in_sp_tab.ele('x://button[normalize-space(.)="确认"]',timeout=2).click()
        sjbm_label = in_sp_tab.ele('x://form//span[normalize-space(.)="商家编码"]',timeout=1)
        sjbm_label.scroll.to_center()
        time.sleep(1)
        for color_index in range(len(color_list)):
            color = color_list[color_index]
            for size_index in range(len(size_list)):
                size = size_list[size_index]
                key = f'{color}-{size}'
                price = default_price
                stock = 0
                sku = ''
                if key in color_size_dic.keys():
                    stock = color_size_dic[key]['stock']
                    sku =  color_size_dic[key]['sku']
                    price =  color_size_dic[key]['price']
                web.xy_input_sku_data(in_sp_tab, color, size, price, stock, sku)


    else:
        # 价格填写
        in_sp_tab.ele("x://label[text()='售价']/..//input").input(goods_price)
        if in_sp_tab.wait.eles_loaded("text:商家编码", timeout=1):
            sku_code_div_ele = in_sp_tab.ele("text:商家编码").parent(3)
            sku_code_div_ele.ele('tag=input').input(sku_code)
    publish_btn = in_sp_tab.ele("立即发布")
    sure_btn = in_sp_tab.ele("x://button//span[text()='确定']")


    # 立即发布勾选
    publish_btn.click()
    sure_btn.click()
    time.sleep(1)
    in_sp_tab.close()

    # 数据返填
    excel.write_csv(goods_id, "闲鱼", xy_dict, fl_text,excel_path)






