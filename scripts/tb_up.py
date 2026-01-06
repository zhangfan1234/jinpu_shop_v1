import os.path
import time
from time import sleep

from DrissionPage import ChromiumPage, ChromiumOptions
import config.jp_data as jp
import utils.file_operations as file
import utils.web_automation as web
import utils.data_processing as data
import utils.excel_operations as excel
from utils.drission_utils import *


def tb_main(tb_dict_list,excel_path,image_path):
    print(f"==================== 淘宝开始上传 共{len(tb_dict_list)}个 ====================")

    # 打开浏览器到千牛, 进入到商品发布页
    co = ChromiumOptions().set_paths(local_port=9999)
    page = ChromiumPage(addr_or_opts=co)
    in_sp_tab = page.new_tab("https://myseller.taobao.com/home.htm/SellManage/all")

    for tb_dict in tb_dict_list:
        # 新建商品页
        print("【淘宝发布商品】点击发布商品按钮")
        sp_tab = in_sp_tab.ele("x://div[@class='l-config-list-toolbar']//a/span[text()='发布商品']").click.for_new_tab()
        try:
            tb_shop_up(sp_tab, tb_dict,excel_path,image_path)
            print(tb_dict['id'], "发布成功")
        except:
            input('发布失败，准备关闭页面')
            sp_tab.close()
            print(tb_dict['id'], "发布失败...")


# 淘宝单商品上传流程
def tb_shop_up(sp_tab, tb_dict,excel_path,image_path):
    # 新建商品页
    print(f"【淘宝发布商品】tb_dict={tb_dict}")
    # sp_tab = in_sp_tab.ele("x://div[@class='l-config-list-toolbar']//a/span[text()='发布商品']").click.for_new_tab()
    # 提取数据
    goods_id = tb_dict['id'].strip()
    goods_name = tb_dict['name']
    goods_desc = tb_dict['desc']
    goods_brand = tb_dict['brand']
    goods_sku_price = tb_dict['sku_price']
    goods_price = tb_dict['price']
    goods_stock = tb_dict['stock']
    sku_code = tb_dict['sku_code']
    print(f"【淘宝发布商品】点击以图发品")
    if not tab_btn_click(sp_tab, 'text:以图发品'):
        time.sleep(1)
        input('怎么没有以图发品：')
        tab_btn_click(sp_tab, 'text:以图发品')
    time.sleep(1)

    # 图片上传
    img_dir_path = os.path.join(image_path,goods_id)  # 商品主图路径
    print(f"【淘宝发布商品】准备打开商品图片img_dir_path={img_dir_path}")
    img_path_list = file.get_filepath_from_dir(img_dir_path, 'jpg')  # 获取商品主图路径下的所有jpg文件路径列表
    print(f"【淘宝发布商品】获取商品图={img_path_list}")
    web.tb_img_up(img_path_list, sp_tab)

    # 类目选择
    img_dir_path_t = img_dir_path + "\\1.jpg"
    lm_name = web.tb_category_input(sp_tab, goods_name, goods_desc, goods_brand, goods_id, goods_price, goods_sku_price,
                                    img_dir_path_t)
    # 填写商品标题
    # goods_name = data.handle_str_length(goods_name, 58)  # 截取标题长度
    if sp_tab.wait.eles_loaded("x://div[@id='struct-title']//input", timeout=1):
        print(f"【淘宝发布商品】填写商品标题={goods_name}")
        sp_tab.ele("x://div[@id='struct-title']//input").input(goods_name)  # 商品标题

    # 淘宝属性填写
    # img_dir_path_t = img_dir_path + "\\1.jpg"
    print("【淘宝发布商品】淘宝类目属性填写")
    web.tb_attribute_input_2(sp_tab, goods_name, goods_desc, goods_brand, goods_id, goods_price, goods_sku_price,
                           img_dir_path_t)
    #
    print(f"【淘宝发布商品】商品类目、商品属性、详情描述填写完毕，确认，下一步")
    if sp_tab.wait.eles_loaded("x://span[text()='确认，下一步']", timeout=3):
        sp_tab.ele("x://span[text()='确认，下一步']").click()

    time.sleep(2)
    # 填写商品标题
    # goods_name = data.handle_str_length(goods_name, 58)  # 截取标题长度
    if sp_tab.wait.eles_loaded("x://div[@id='struct-title']//input", timeout=1):
        print(f"【淘宝发布商品】填写商品标题={goods_name}")
        sp_tab.ele("x://div[@id='struct-title']//input").input(goods_name)  # 商品标题

    print("【淘宝发布商品】淘宝类目属性填写")
    web.tb_attribute_input_2(sp_tab, goods_name, goods_desc, goods_brand, goods_id, goods_price, goods_sku_price,
                             img_dir_path_t)


    # 淘宝规格填写
    print("【淘宝发布商品】淘宝规格填写")
    web.tb_spec_input(sp_tab, goods_sku_price, goods_stock, goods_price, sku_code, goods_id)
    # 物流信息 48小时内发货
    print("【淘宝发布商品】选择48小时内发货")
    if sp_tab.wait.eles_loaded('48小时内发货', timeout=2):
        sp_tab.ele("48小时内发货").click()
        time.sleep(1)
        # 随便点一下
        tab_btn_click(sp_tab, '发货时效')
        time.sleep(1)
    if sp_tab.wait.eles_loaded('text:大陆及港澳台', timeout=2):
        sp_tab.ele("text:大陆及港澳台").click()
        time.sleep(1)
        # 随便点一下
        tab_btn_click(sp_tab, '发货时效')
        time.sleep(1)

    # print("【淘宝发布商品】提取方式选择使用物流配送")
    if sp_tab.wait.eles_loaded('text=使用物流配送', timeout=2):
        try_count = 0
        while True:
            try_count += 1
            tab_btn_click(sp_tab, 'text:使用物流配送')
            time.sleep(2)
            # 随便点一下
            tab_btn_click(sp_tab, '发货时效')
            time.sleep(2)
            send_temp_input_ele = sp_tab.ele('.child-block logis-block')
            send_temp_sel_ele_click_result = tab_btn_click(send_temp_input_ele, '.next-select-values next-input-text-field')
            print(f'选择物流点击结果={send_temp_sel_ele_click_result}')
            if not send_temp_sel_ele_click_result:
                if try_count == 3:
                    break
                continue
            time.sleep(2)
            tab_btn_click(sp_tab, '@title=包邮')
            time.sleep(1)
            break


    # 淘宝详情处理
    print("【淘宝发布商品】淘宝详情处理")
    web.tb_detail_handle(sp_tab, goods_desc, img_path_list)
    time.sleep(3)

    # 提交发布退出
    print("【淘宝发布商品】提交宝贝信息")
    sp_tab.ele("提交宝贝信息").click()
    if sp_tab.wait.eles_loaded("比例不符合要求", timeout=3):
        print("【淘宝发布商品】比例不符合要求")
        for ele in sp_tab.eles("x:(//div[@class='image-list'])[1]/div[@class='drag-item']"):
            sleep(1)
            ele.hover()
            sleep(1)
            sp_tab.ele("x://div[@title='删除']").click()
            web.tb_pust_zt(sp_tab, len(img_path_list))

        sleep(2)
        sp_tab.ele("提交宝贝信息").click()
    if sp_tab.wait.eles_loaded("主图不能为空", timeout=3):
        print("【淘宝发布商品】主图不能为空")
        web.tb_pust_zt(sp_tab, len(img_path_list))

        sleep(2)
        sp_tab.ele("提交宝贝信息").click()
    if sp_tab.wait.eles_loaded("x://span[text()='继续发布']"):
        print("【淘宝发布商品】继续发布，关闭当前tab页面")
        # 关闭
        sp_tab.close()
    # 数据返填
    print("【淘宝发布商品】数据返填，更新excel")
    input("发布成功！")
    excel.write_csv(goods_id, "淘宝", tb_dict, lm_name,excel_path)
