import ezdxf
import json

def serialize_entity(entity):
    data = entity.dxfattribs()
    # Convert Vec3 objects to lists
    for key, value in data.items():
        if isinstance(value, ezdxf.math.Vec3):
            data[key] = [value.x, value.y, value.z]
    return data

# 读取DXF文件
doc = ezdxf.readfile('01栈桥平台总体布置图20240521.dxf')

# 存储所有信息的字典
dxf_data = {
    'layers': {},
    'blocks': {},
    'entities': [],
    'annotations': []
}

# 获取所有层信息
for layer in doc.layers:
    layer_info = {
        'name': layer.dxf.name,
        'color': layer.color,
        'linetype': layer.dxf.linetype,
        'is_off': layer.is_off(),
        'is_frozen': layer.is_frozen()
    }
    dxf_data['layers'][layer.dxf.handle] = layer_info

# 获取所有块信息
for block in doc.blocks:
    block_info = {
        'name': block.name,
        'entities': []
    }
    for entity in block:
        block_info['entities'].append({
            'type': entity.dxftype(),
            'data': serialize_entity(entity)
        })
    dxf_data['blocks'][block.dxf.handle] = block_info

# 获取所有实体信息
for entity in doc.modelspace():
    entity_info = {
        'type': entity.dxftype(),
        'layer': entity.dxf.layer,
        'data': serialize_entity(entity)
    }
    dxf_data['entities'].append(entity_info)

# 获取所有注释信息
for entity in doc.modelspace().query('TEXT'):
    annotation_info = {
        'text': entity.dxf.text,
        'position': [entity.dxf.insert.x, entity.dxf.insert.y, entity.dxf.insert.z],
        'height': entity.dxf.height,
        'layer': entity.dxf.layer
    }
    dxf_data['annotations'].append(annotation_info)

# 将信息写入JSON文件
with open('dxf_data.json', 'w', encoding='utf-8') as f:
    json.dump(dxf_data, f, ensure_ascii=False, indent=4, default=str)

print("DXF数据已写入 dxf_data.json 文件")
