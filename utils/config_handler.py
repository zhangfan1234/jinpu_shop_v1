# 默认输入函数
def input_default(prompt, default):
    """
    输入函数, 如果输入为空, 则返回默认值
    :param prompt:  输入提示
    :param default:  默认值
    :return:  用户输入的信息/默认值
    """
    result = input(f"{prompt} (默认是 {default}): ")
    if result == '':
        return default
    else:
        return result


#  异常输入重试
def input_try(prompt, on_all):
    """
    判断用户输入的适合符合提示需要的, 不符合将提示重新输入
    :param prompt: 提示词
    :param on_all: 模式, 1为单选, 2为多选
    :return: 返回用户合法的输入
    """

    while True:
        is_true = True
        # 获取用户输入的数据
        user_input = input(prompt)

        # 单选模式
        if on_all == 1:
            if len(user_input) != 1:
                print("输入有误, 请重新输入")
                continue
            else:
                if user_input not in prompt:
                    print("输入有误, 请重新输入")
                    continue

        # 多选模式
        if on_all == 2:
            for i in user_input:
                if prompt.find(i) == -1:
                    print("输入有误, 请重新输入")
                    is_true = False
                    break

        # 判断退出
        if is_true:
            break
        else:
            continue

    return user_input


# 指定内容写入到配置文件, 不删除原有内容, 如果有关键词存在, 则替换, 如果没有, 则追加
def write_to_config(config_path, key, value, illustrate):
    """
    :param config_path:  配置文件路径
    :param key:  配置文件中的键
    :param value:  配置文件中的值
    :param illustrate:  配置文件中的注释
    :return:
    """
    with open(config_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    with open(config_path, "w", encoding="utf-8") as f:
        for line in lines:
            is_true = False
            if line.startswith("MAIN_PATH"):
                input_text = f"{key} = '{value}'  # {illustrate}\n"
                f.write(input_text)
                is_true = True
                break
            f.write(line)
        if not is_true:
            # 读取写入文件内容
            f.writelines(lines)
            # 写入新内容
            f.write(f"{key} = '{value}'  # {illustrate}\n")