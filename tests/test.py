from DrissionPage import ChromiumPage, ChromiumOptions

# 删除销售属性信息
co = ChromiumOptions().set_paths(local_port=9999)
page = ChromiumPage(addr_or_opts=co)
sp_tab = page.new_tab('https://item.upload.taobao.com/sell/v2/publish.htm?catId=50010159&gpfRenderTrace=2150471817364957762218717e0dd4&fromAIImage=true&keyProps=%7B%22p-20000%22%3A%7B%22value%22%3A3395518%2C%22text%22%3A%22Billabong%22%7D%7D&fromAIPublish=true&newRouter=1&paramCacheId=merge_router_cache_1094121856_1736495810173_860&x-gpf-submit-trace-id=2150471817364958101055727e0dd4')
input("等待输入：")
goods_arrt_tr_ele = sp_tab.ele(f"xpath://tr[@class='sku-table-row'][1]")
row_idx = 1
while True:
    page_goods_color = goods_arrt_tr_ele.child(index=1).text
    page_goods_size = goods_arrt_tr_ele.child(index=2).text
    print(f'第{row_idx}行商品规格，颜色={page_goods_color}, 尺寸={page_goods_size}')
    try:
        goods_arrt_tr_ele = goods_arrt_tr_ele.next(timeout=2)
    except:
        goods_arrt_tr_ele = None
    if goods_arrt_tr_ele is None:
        break
    row_idx += 1
input("程序暂停：")