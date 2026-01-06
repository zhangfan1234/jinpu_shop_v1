# -*- coding: utf-8 -*-
'''
@Time    : 2025-11-16 09:46
@Author  : AnTi
@File    : test.py
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple ccxt
'''
import multiprocessing
import os
import sys
import config.jp_data as jp
import utils.config_handler as config
import utils.excel_operations as excel
import scripts.tb_up as tb
import scripts.xy_up as xy
import scripts.wd_up as wd
from datetime import datetime
from DrissionPage import ChromiumPage, ChromiumOptions


# 用户输入数据初始化
def user_input_ui():
    # 输入主文件夹路径
    # nwe_main_path = config.input_default("请输入主文件夹路径：", main_path)
    # # 如果路径修改了, 更新配置文件
    # if nwe_main_path != main_path:
    #     config.write_to_config(r"config/jp_data.py", "MAIN_PATH", nwe_main_path, "主文件夹路径")

    # 商品发布的平台
    platform_list = []
    platform = config.input_try("请输入本次上传的平台, 1.淘宝, 2.闲鱼, 3.微店：", 2)


    if "1" in platform:
        platform_list.append("淘宝")
    if "2" in platform:
        platform_list.append("闲鱼")
    if "3" in platform:
        platform_list.append("微店")

    print("发布的门店为: ", platform_list)

    # 浏览器初始化
    co = ChromiumOptions().set_paths(local_port=9999)
    page = ChromiumPage(addr_or_opts=co)
    for i in platform_list:
        if i == "淘宝":
            page.new_tab("https://loginmyseller.taobao.com/")
        if i == "闲鱼":
            # 打开闲鱼网站
            page.new_tab("https://goofish.pro/sale/product/all")
        if i == "微店":
            # 打开微店网站
            page.new_tab("https://d.weidian.com/weidian-pc/weidian-loader/#/pc-vue-item-list/item/list")

    # 让用户确定是否开始上传
    config.input_try("请确保发布的平台处于登录状态(输入: y)确定: ", 1)

    return platform_list


def main():

    # 获取用户输入数据
    platform_list = user_input_ui()

    # 获取表格路径
    excel_path = '津铺商品库.xlsm'
    image_path = '商品主图'
    # 表格数据处理成[dict,dict] 各平台待发布数据
    tb_dict_list, xy_dict_list, wd_dict_list = excel.read_csv_to_dict(excel_path)

    # 分别调用不同平台发布
    for platform in platform_list:
        if platform == "淘宝":
            print(tb_dict_list)
            start = datetime.today()
            tb.tb_main(tb_dict_list,excel_path,image_path)
            end = datetime.today()
            print(f"淘宝发布数量{len(tb_dict_list)}, 发布耗时: {end - start}")

        if platform == "闲鱼":
            print(f'xy_dict_list={xy_dict_list}')
            start = datetime.today()
            xy.xy_main(xy_dict_list,excel_path,image_path)
            end = datetime.today()
            print(f"闲鱼发布数量{len(xy_dict_list)}, 发布耗时: {end - start}")

        if platform == "微店":
            print(wd_dict_list)
            start = datetime.today()
            wd.wd_main(wd_dict_list,excel_path,image_path)
            end = datetime.today()
            print(f"微店发布数量{len(wd_dict_list)}, 发布耗时: {end - start}")



if __name__ == "__main__":
    main()