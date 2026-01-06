import json


def extract_categories(data, parent_path=""):
    """
    递归提取所有叶子类目，构建完整路径
    """
    result = []
    for item in data:
        current_path = f"{parent_path}/{item['label']}" if parent_path else item['label']
        if 'children' in item and item['children']:
            # 递归处理子节点
            result.extend(extract_categories(item['children'], current_path))
        else:
            # 叶子节点，添加到结果中
            result.append(current_path)
    return result


def process_category_file(input_file, output_file):
    """
    处理原始TXT文件，提取类目路径并输出
    """
    # 读取原始文件
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # 解析JSON
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        print("错误：文件内容不是有效的JSON格式")
        return

    # 提取所有叶子类目
    all_categories = []
    if 'data' in data:
        for category in data['data']:
            if 'children' in category:
                all_categories.extend(extract_categories(category['children'], category['label']))

    # 写入输出文件
    with open(output_file, 'w', encoding='utf-8') as f:
        for category in all_categories:
            f.write(category + '\n')

    print(f"处理完成！共提取 {len(all_categories)} 个类目。")
    print(f"结果已保存到: {output_file}")


# 使用示例
if __name__ == "__main__":
    input_file = "类目JSON.txt"  # 输入文件名
    output_file = "闲鱼管家类目.txt"  # 输出文件名

    process_category_file(input_file, output_file)