import os
from ruamel.yaml import YAML

def merge_yaml(file1, file2):  # 只传入两个文件参数
    yaml = YAML()
    yaml.indent(mapping=2, sequence=4, offset=2)
    files_exist = [os.path.exists(file) for file in [file1, file2]]

    if not all(files_exist):
        print("一个或多个文件路径无效")
        return None

    try:
        with open(file1, 'r', encoding='utf-8') as f1, \
             open(file2, 'r', encoding='utf-8') as f2:
            data1 = yaml.load(f1)
            data2 = yaml.load(f2)
    except Exception as e:
        print(f"YAML文件处理错误: {e}")
        return None

    # 使用 ruamel.yaml 合并 YAML 文件
    merged_data = yaml.load("{}")
    for key in ['proxies', 'proxy-groups', 'rules']:
        if key in data1:
            merged_data[key] = data1[key]
        if key in data2:
            if key not in merged_data:
                merged_data[key] = []
            merged_data[key].extend(data2[key])

    # 去重 proxies
    if 'proxies' in merged_data:
        merged_data['proxies'] = list({v['name']:v for v in merged_data['proxies']}.values())

    # 去重 proxy-groups
    if 'proxy-groups' in merged_data:
        group_dict = {group['name']: group for group in merged_data['proxy-groups']}
        for group_list in [data1, data2]:  # 只遍历两个文件
            for group in group_list.get('proxy-groups', []):
                name = group['name']
                if name in group_dict:
                    existing_group = group_dict[name]
                    existing_group['proxies'] = list(set(existing_group['proxies'] + group['proxies']))
                else:
                    group_dict[name] = group
        merged_data['proxy-groups'] = list(group_dict.values())

    # 去重 rules
    if 'rules' in merged_data:
        merged_data['rules'] = list(set(merged_data['rules']))

    return yaml.dump(merged_data)

if __name__ == "__main__":
    file1 = './configs/config1.yaml'
    file2 = './configs/config2.yaml'
    # file3 = './configs/config3.yaml'  # 移除 file3
    merged_yaml = merge_yaml(file1, file2)  # 只传入两个文件
    if merged_yaml:
        with open('./configs/config_merged.yaml', 'w', encoding='utf-8') as f:
            f.write(merged_yaml)
        print("YAML文件合并完成，已保存到 ./configs/config_merged.yaml")
    else:
        print("YAML合并失败")
