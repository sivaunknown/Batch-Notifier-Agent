import json
from dependency_mapper import build_map

# xml_path = r"E:\Batch Notifier\ds_config\ctm_data.xml"

def load_dependency_map(xml_path):
    dependency_map = build_map(xml_path)
    with open('E:/Batch Notifier/config/dependency_map.json', 'w', encoding='utf-8') as f:
        json.dump(dependency_map, f, indent=4)
    print("Dependency map generated successfully!")
