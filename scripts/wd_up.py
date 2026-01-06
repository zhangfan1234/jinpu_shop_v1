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
import config.jp_data as jp
import utils.file_operations as file
import utils.excel_operations as excel


def wd_main(wd_dict_list,excel_path,image_path):
    print(f"==================== 微店开始上传 共{len(wd_dict_list)}个 ====================")

    # 打开浏览器到微店, 进入到商品发布页
    co = ChromiumOptions().set_paths(local_port=9999)
    page = ChromiumPage(addr_or_opts=co)
    in_sp_tab = page.new_tab("https://d.weidian.com/weidian-pc/weidian-loader/#/pc-vue-item-list/item/list")


    for wd_dict in wd_dict_list:
        # 新建商品页
        wd_tab = in_sp_tab.ele("x://span[text()='添加商品']").click.for_new_tab()
        try:
            wd_shop_up(wd_tab, wd_dict,excel_path,image_path)
            print(wd_dict['id'], "发布成功")
        except Exception as ex:
            wd_tab.close()
            print(wd_dict['id'], "发布失败...")


def wd_shop_up(wd_tab, wd_dict,excel_path,image_path):
    # 新建商品页
    # wd_tab = in_sp_tab.ele("x://span[text()='添加商品']").click.for_new_tab()

    # 提取数据
    goods_id = wd_dict['id'].strip()
    goods_name = wd_dict['name']
    goods_desc = wd_dict['desc']
    goods_brand = wd_dict['brand']
    goods_sku_price = wd_dict['sku_price']
    goods_stock = wd_dict['stock']
    goods_price = wd_dict['price']
    sku_code = wd_dict['sku_code']
    # 上传图片
    img_dir_path = os.path.join(image_path,goods_id)  # 商品主图路径
    print(f'【微店】上传图片img_dir_path={img_dir_path}')
    img_path_list = file.get_filepath_from_dir(img_dir_path, 'jpg')  # 获取商品主图路径下的所有jpg文件路径列表
    web.wd_img_up(img_path_list, wd_tab)

    # 填写标题
    print('【微店】填写标题')
    wd_tab.ele("x://div[@class='title-container']//textarea").input(goods_name)

    # 类目选择
    print('【微店】类目选择')
    img_path_t = img_dir_path + "\\1.jpg"
    lm_text = web.wd_category_input(wd_tab, goods_name, goods_desc, img_path_t)


    # 价格库存填写
    # 库存列表
    stock_list = str(goods_stock).split(',')
    sku_code_list = sku_code.split(',')
    goods_sku_price_list = goods_sku_price.split(',')
    #这个是多库存输入
    if len(goods_sku_price_list) > 1 and len(stock_list) == len(goods_sku_price_list):
        mutil_spec_radio = wd_tab.ele("多级型号")
        mutil_spec_radio.scroll.to_center()

        mutil_spec_radio.click()
        time.sleep(0.5)
        mutil_spec_radio.click()
        time.sleep(1)
        corlor_btn = wd_tab.ele('x://div[normalize-space(.)="颜色"]')
        corlor_btn.click()
        color_list= []
        for i in range(len(goods_sku_price_list)):
            time.sleep(0.5)
            color_size_price_tuple = goods_sku_price_list[i].split(":")
            color = color_size_price_tuple[0]
            if color not in color_list:
                wd_tab.ele(f'x://div[normalize-space(.)="{color}"]').click()
                color_list.append(color)

        time.sleep(0.5)
        wd_tab.ele(f'x://button[starts-with(normalize-space(.), "添加")][contains(@class, "btn")]').click()
        time.sleep(0.5)
        wd_tab.ele("尺码").click()

        size_list = []
        for i in range(len(goods_sku_price_list)):
            time.sleep(0.5)
            color_size_price_tuple = goods_sku_price_list[i].split(":")
            size = color_size_price_tuple[1]
            if size not in size_list:
                wd_tab.ele(f'x://div[normalize-space(.)="{color_size_price_tuple[1]}"]').click()
                size_list.append(size)
        time.sleep(0.5)
        wd_tab.ele(f'x://button[starts-with(normalize-space(.), "添加")][contains(@class, "btn")]').click()

        for i in range(len(goods_sku_price_list)):
            time.sleep(0.5)
            color_size_price_tuple = goods_sku_price_list[i].split(":")
            color = color_size_price_tuple[0]
            size  = color_size_price_tuple[1]
            price = color_size_price_tuple[2]
            stock = stock_list[i]
            sku = sku_code_list[i]
            web.wd_input_sku_data(wd_tab,color,size,price,stock,sku)
    else:
        print('【微店】价格库存填写')
        wd_tab.ele("x://input[@placeholder='请填写商品价格']").input(goods_price, clear=True)

        stock = sum([int(i) for i in stock_list])
        wd_tab.ele("x://input[@placeholder='请填写商品库存']").input(stock, clear=True)
        time.sleep(1)

    wd_tab.ele("x://input[@placeholder='选填，用于商家系统对接']").input(sku_code, clear=True)

    # 下一步
    print('【微店】下一步')
    time.sleep(1)
    wd_tab.ele("下一步").click()

    # 商品详情
    print('【微店】商品详情')
    web.wd_detail_handle(wd_tab, goods_desc)
    # 创建
    print('【微店】点击创建')
    wd_tab.ele("x://span[text()='创建']").click()
    time.sleep(1)
    # 关闭页面
    if wd_tab.wait.eles_loaded("x://div[@class='title-container']//textarea"):
        wd_tab.close()
    # 数据返填
    excel.write_csv(goods_id,"微店", wd_dict, lm_text,excel_path)