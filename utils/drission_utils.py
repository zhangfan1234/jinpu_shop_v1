from DrissionPage import ChromiumPage, ChromiumOptions

def get_tab_chrome() -> ChromiumPage:
    co = ChromiumOptions()
    co.auto_port()
    return ChromiumPage(co)

def tab_btn_click(tab, locator):
    try:
        btn_ele = tab.ele(locator, timeout=3)
        btn_ele.click()
        return True
    except Exception as e:
        return False

def tab_get_inner_html(tab, locator, timeout = 2):
    try:
        page_ele = tab.ele(locator, timeout=timeout)
        text = page_ele.inner_html
        return text
    except Exception as e:
        return None

def tab_get_text(tab, locator, timeout = 2):
    try:
        page_ele = tab.ele(locator, timeout=timeout)
        text = page_ele.text
        return text
    except Exception as e:
        return ''

def tab_input_content(tab, locator, content):
    try:
        input_ele = tab.ele(locator)
        input_ele.clear()
        input_ele.input(content)
        return True
    except Exception as e:
        return False
