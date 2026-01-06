import os


# 获取指定目录下的文件路径, 是否包含子目录下的特定文件
def get_filepath_from_dir(dirpath,extension, include_subdirectories=False):
    """
    获取指定目录下所有特定扩展名的文件路径, 是否包含子文件夹下的文件

    Args:
        directory (str): 需要搜索的目录路径
        extension (str): 文件扩展名
        include_subdirectories (bool): 是否包含子文件夹下的文件
    Returns:
        list: 所有特定扩展名文件的完整路径列表
    """

    files_with_extension = []

    if include_subdirectories:
        for root, dirs, files in os.walk(dirpath):
            for file in files:
                if file.endswith(f".{extension}"):
                    files_with_extension.append(os.path.join(root, file))
    else:
        for file in os.listdir(dirpath):
            if file.endswith(f".{extension}"):
                files_with_extension.append(os.path.join(dirpath, file))

    # 返回所有特定扩展名文件的完整路径列表
    return files_with_extension
