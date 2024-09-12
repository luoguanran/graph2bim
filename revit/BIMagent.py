def create_level(elevation, level_name=""):
    """
    创建标高
    :param
        level_name(string): 标高平面的名称，默认为空
        elevation(float): 高程，单位为mm
    :return
        code(int): 状态代码
        message(str): 执行信息
        level_id(int): 创建的标高id
    """
    script = f'''import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
clr.AddReference('System')
from Autodesk.Revit.DB import *
t = Transaction(doc, 'Create Level')

try:
    t.Start()

    level = Level.Create(doc, {elevation}/304.8)
    level_name_param = level.get_Parameter(BuiltInParameter.DATUM_TEXT)
    level_name = '{level_name}'

    if level_name:
        level_name_param.Set(level_name)

    t.Commit()

    result = {{
        'code': 200,
        'message': 'Level created successfully',
        'level_id': level.Id.IntegerValue
    }}

except Exception as e:
    if t.HasStarted():
        t.RollBack()
    result = {{
        'code': 500,
        'message': str(e),
        'level_id': None
    }}'''
    return script


def create_grid(start_point, end_point, grid_name=""):
    """
    创建直线轴网
    :param
        grid_name(string): 轴网的名称，默认为空
        start_point(array): 起点坐标(x, y, z)
        end_point(array): 终点坐标(x, y, z)
    :return
        code(int): 状态代码
        message(str): 执行信息
        grid_id(int): 创建的轴网id
    """
    script = f'''import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
clr.AddReference('System')
from Autodesk.Revit.DB import *
t = Transaction(doc, 'Create Grid')

try:
    # Set coordinates
    start_point = XYZ({start_point[0]}, {start_point[1]}, {start_point[2]})
    end_point = XYZ({end_point[0]}, {end_point[1]}, {end_point[2]})

    # Create a Line
    line = Line.CreateBound(start_point, end_point)

    # Commit the transaction
    t.Start()

    # Create an Grid
    grid = Grid.Create(doc, line)

    # Set the Grid name
    g_name = grid.get_Parameter(BuiltInParameter.DATUM_TEXT)
    g_name.Set("{grid_name}")

    t.Commit()
    result = {{
        'code': 200,
        'message': 'Grid created successfully',
        'grid_id': grid.Id.IntegerValue
    }}

except Exception as e:
    # Rollback the transaction and return error message
    if t.HasStarted():
        t.RollBack()
    result = {{
        'code': 500,
        'message': str(e),
        'grid_id': None
    }}
'''
    return script


def create_column(base_level_id, top_level_id, location_point, width=0, height=0):
    """
    创建结构柱
    :param
        base_level_id(int): 基准标高的ID
        top_level_id(int): 顶部标高的ID
        location_point(tuple): 结构柱的位置点，格式为(x, y)
        width(float): 可选，结构柱的宽度，单位为mm
        height(float): 可选，结构柱的高度，单位为mm
    :return
        code(int): 状态代码
        message(str): 执行信息
        column_id(int): 创建的结构柱id
    """
    script = f'''import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
clr.AddReference('System')
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import *

# 函数定义
def get_element_by_id(element_id):
    return doc.GetElement(ElementId(element_id))

t = Transaction(doc, 'Create Structural Column')

try:
    t.Start()

    # 获取柱类型
    collector = FilteredElementCollector(doc).OfClass(FamilySymbol).OfCategory(BuiltInCategory.OST_StructuralColumns)
    column_type = collector.FirstElement()
    if not column_type:
        raise Exception('No structural column type found')

    # 获取标高
    base_level = doc.GetElement(ElementId({base_level_id}))
    top_level = doc.GetElement(ElementId({top_level_id}))
    if not base_level or not top_level:
        raise Exception('Base level or top level not found')

    # 激活柱类型
    if not column_type.IsActive:
        column_type.Activate()
        doc.Regenerate()

    # 创建柱子
    column_location = XYZ({location_point[0]}/304.8, {location_point[1]}/304.8, 0)
    column = doc.Create.NewFamilyInstance(column_location, column_type, base_level, StructuralType.Column)

    # 设置柱子的高度
    column.get_Parameter(BuiltInParameter.FAMILY_BASE_LEVEL_PARAM).Set(base_level.Id)
    column.get_Parameter(BuiltInParameter.FAMILY_TOP_LEVEL_PARAM).Set(top_level.Id)

    # 设置柱子的宽度和高度（如果有相关参数的话）
    column_width_param = column.get_Parameter(BuiltInParameter.COLUMN_WIDTH)
    column_height_param = column.get_Parameter(BuiltInParameter.COLUMN_HEIGHT)
    if column_width_param and width != 0:
        column_width_param.Set({width}/304.8)
    if column_height_param and height != 0:
        column_height_param.Set({height}/304.8)

    t.Commit()

    result = {{
        'code': 200,
        'message': 'Column created successfully',
        'column_id': column.Id.IntegerValue
    }}

except Exception as e:
    if t.HasStarted():
        t.RollBack()
    result = {{
        'code': 500,
        'message': str(e),
        'column_id': None
    }}
'''
    return script


def create_base_point(base_point):
    """
    设置项目基点
    :param
        base_point(array): 基点坐标(x, y, z)
    :return
        code(int): 状态代码
        message(str): 执行信息
    """
    script = f'''import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
clr.AddReference('System')
from Autodesk.Revit.DB import *
t = Transaction(doc, 'Set Base Point')

try:
    # Get the project base point
    project_base_point = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_ProjectBasePoint).FirstElement()
    if not project_base_point:
        raise Exception("Project Base Point not found")

    # Get the current base point's minimum bounding box
    p_base_point = project_base_point.get_BoundingBox(None).Min

    # Start the transaction
    t.Start()

    # Set the base point coordinates
    project_base_point.get_Parameter(BuiltInParameter.BASEPOINT_EASTWEST_PARAM).Set({base_point[0]})
    project_base_point.get_Parameter(BuiltInParameter.BASEPOINT_NORTHSOUTH_PARAM).Set({base_point[1]})
    project_base_point.get_Parameter(BuiltInParameter.BASEPOINT_ELEVATION_PARAM).Set({base_point[2]})

    # Commit the transaction
    t.Commit()

    # Prepare the result data
    result = {{
        "code": 200, 
        "message": "Base point set successfully"
    }}

except Exception as e:
    # Rollback the transaction and return error message
    if t.HasStarted():
        t.RollBack()
    result = {{
        'code': 500,
        'message': str(e)
    }}

'''
    return script


def create_column_from_family(column_family_name, x=0, y=0, base_level=-1):
    """
    从族库中创建指定名称的柱，需要先创建标高
    :param
        column_family_name(string): 柱的族名
        x(float): 柱的x坐标
        y(float): 柱的y坐标
        base_level(float): 柱所在的标高
    :return
        code(int): 状态代码
        message(str): 执行信息
        column_id(int): 创建的柱id
    """
    script = f'''import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
clr.AddReference('System')
from Autodesk.Revit.DB import *
t = Transaction(doc, 'Create Column from Family')

try:
    # Collect all column types and levels
    columns = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_StructuralColumns).WhereElementIsElementType().ToElements()
    levels = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Levels).WhereElementIsNotElementType().ToElements()

    # Find the correct level
    for level in levels:
        elevation = level.get_Parameter(BuiltInParameter.LEVEL_ELEV).AsDouble()
        if elevation == {base_level}/304.8:
            level_0 = level
            break
        if elevation == -1:
            level_0 = levels[0]
            break

    # Find the correct column type
    column_type = None
    for column in columns:
        col_name = column.get_Parameter(BuiltInParameter.SYMBOL_NAME_PARAM).AsString()
        if col_name == '{column_family_name}':
            column_type = column
            break

    if column_type is None:
        raise Exception("Column type not found")

    # Start the transaction
    t.Start()

    # Create the column instance
    col = doc.Create.NewFamilyInstance(XYZ({x}, {y}, level_0.Elevation), column_type, level_0, Structure.StructuralType.Column)

    # Set the top offset
    top_offset = col.get_Parameter(BuiltInParameter.FAMILY_TOP_LEVEL_OFFSET_PARAM)
    top_offset.Set(level_0.Elevation/304.8)

    # Commit the transaction
    t.Commit()

    # Prepare the result data
    result = {{
        "code": 200, 
        "message": "Column created successfully", 
        "column_id": col.Id.IntegerValue
    }}

except Exception as e:
    # Rollback the transaction and return error message
    if t.HasStarted():
        t.RollBack()
    result = {{
        "code": 500, 
        "message": str(e),
        "column_id": None
    }}

'''
    return script


def create_rectangular_column(base_point, length, width, height):
    """
    创建自定义的矩形柱
    :param
        base_point(array): 基点坐标(x,y,z)
        length(float): 柱的长度/mm
        width(float): 柱的宽度/mm
        height(float): 柱的高度/mm
    :return
        code(int): 状态代码
        message(str): 执行信息
        element_id(list): 创建的元素id
    """
    script = f'''import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
clr.AddReference('System')
from Autodesk.Revit.DB import *
t = Transaction(doc, 'Create Rectangular Column')

try:
    # Start the transaction
    t.Start()

    # Convert dimensions from mm to feet
    length = {length} / 304.8
    width = {width} / 304.8
    height = {height} / 304.8
    base_point = {base_point}

    # Define base points
    pt1 = XYZ(base_point[0], base_point[1], base_point[2])
    pt2 = XYZ(base_point[0] + length, base_point[1], base_point[2])
    pt3 = XYZ(base_point[0] + length, base_point[1] + width, base_point[2])
    pt4 = XYZ(base_point[0], base_point[1] + width, base_point[2])

    # Create boundary lines
    line1 = Line.CreateBound(pt1, pt2)
    line2 = Line.CreateBound(pt2, pt3)
    line3 = Line.CreateBound(pt3, pt4)
    line4 = Line.CreateBound(pt4, pt1)

    # Create the base loop
    base_loop = CurveLoop()
    base_loop.Append(line1)
    base_loop.Append(line2)
    base_loop.Append(line3)
    base_loop.Append(line4)

    # Create the extrusion geometry
    solid = GeometryCreationUtilities.CreateExtrusionGeometry([base_loop], XYZ.BasisZ, height)

    # Create the direct shape
    direct_shape = DirectShape.CreateElement(doc, ElementId(BuiltInCategory.OST_StructuralColumns))
    direct_shape.SetShape([solid])

    # Commit the transaction
    t.Commit()

    # Prepare the result data
    result = {{
        "code": 200,
        "message": "Rectangular column created successfully",
        "element_id": direct_shape.Id.IntegerValue
    }}

except Exception as e:
    # Rollback the transaction and return error message
    if t.HasStarted():
        t.RollBack()
    result = {{
        "code": 500,
        "message": str(e),
        "element_id": None
    }}
'''
    return script


def delete_element(element, is_element_type=False):
    """
    删除指定元素实例或类型
    :param
        element(string): 元素名称，为BuiltInCategory枚举类
        is_element_type(bool): 删除的元素是否为类型，默认为False
    :return
        code(int): 状态代码
        message(str): 执行信息
        deleted_ids(list): 删除的元素id
    """
    script = f'''import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
clr.AddReference('System')
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import *

is_element_type = {is_element_type}
elements = FilteredElementCollector(doc).OfCategory(BuiltInCategory.{element})
if is_element_type:
    elements = elements.WhereElementIsElementType().ToElements()
else:
    elements = elements.WhereElementIsNotElementType().ToElements()

t = Transaction(doc, 'Delete {element}')
t.Start()

try:
    deleted_ids = []
    for elem in elements:
        doc.Delete(elem.Id)
        deleted_ids.append(elem.Id.IntegerValue)
    t.Commit()
    result = {{
        "code": 200,
        "message": "Instances have been deleted successfully",
        "deleted_ids": deleted_ids
    }}
except Exception as e:
    if t.HasStarted():
        t.RollBack()
    result = {{
        "code": 500,
        "message": str(e),
        "deleted_ids": None
    }}
'''
    return script


def select_element(element, is_element_type=False):
    """
    搜索并显示指定元素实例或类型
    :param
        element(string): 元素名称，为BuiltInCategory枚举类
        is_element_type(bool): 删除的元素是否为类型，默认为False
    :return
        code(int): 状态代码
        message(str): 执行信息
        element_ids(list): 搜索的元素id
    """
    script = f"""import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
clr.AddReference('System')
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import *
from System.Collections.Generic import List

try:
    collector = FilteredElementCollector(doc)
    element_filter = ElementCategoryFilter(BuiltInCategory.{element})
    elements = collector.WherePasses(element_filter)

    if {is_element_type}:
        elements = elements.WhereElementIsElementType().ToElements()
    else:
        elements = elements.WhereElementIsNotElementType().ToElements()

    element_ids = List[ElementId]()
    instance_info = ''
    for elem in elements:
        element_ids.Add(elem.Id)
        instance_info += 'ID: ' + str(elem.Id.IntegerValue) + ', Name: ' + str(elem.Name) + '\\n'

    # Prepare the result data
    if element_ids.Count > 0:
        uidoc.Selection.SetElementIds(element_ids)
        result = {{
            "code": 200,
            "message": "Found and selected elements",
            "element_ids": [id.IntegerValue for id in element_ids]
        }}
    else:
        result = {{
            "code": 500,
            "message": "No element instances found.",
            "element_ids": []
        }}
except Exception as e:
    result = {{
        "code": 500,
        "message": str(e),
        "element_ids": []
    }}
"""
    return script


def create_element(element, x=0, y=0, z=0):
    """
    创建实例
    :param
        element(string): 实例名称
        x(float): 实例的x坐标
        y(float): 实例的y坐标
        base_level(float): 实例的z坐标
    :return
        code(int): 状态代码
        message(str): 执行信息
        element_id(int): 创建的实例id
    """
    script = f"""import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
clr.AddReference('System')
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import *

create_element_name = "{element}"

collector = FilteredElementCollector(doc).OfClass(FamilySymbol)
t = Transaction(doc, "Create Element")

try:
    family_symbol = None
    for symbol in collector:
        if symbol.Name == create_element_name:
            family_symbol = symbol
            break

    if family_symbol:
        if not family_symbol.IsActive:
            family_symbol.Activate()
            doc.Regenerate()

        location_point = XYZ({x}, {y}, {z})
        t.Start()
        new_element = doc.Create.NewFamilyInstance(location_point, family_symbol, Structure.StructuralType.NonStructural)
        t.Commit()

        result = {{
            "code": 200,
            "message": "Instance created successfully",
            "element_id": new_element.Id.IntegerValue
        }}
        TaskDialog.Show("Success", "Instance has been created")
    else:
        result = {{
            "code": 404,
            "message": "Instance type doesn't exist",
            "element_id": None
        }}
        TaskDialog.Show("Error", "Instance type doesn't exist")

except Exception as e:
    if t.HasStarted():
        t.RollBack()
    result = {{
        "code": 500,
        "message": str(e),
        "element_id": None
    }}
    TaskDialog.Show("Error", str(e))
"""
    return script


def get_level_by_name(level_name):
    """
    根据层级的名称获取层级的ID
    :param
        level_name(str): 标高/层高的名称。
    :return
        element_id(int): 层级的ID，如果未找到则返回None。
    """
    script = f"""import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
clr.AddReference('System')
from Autodesk.Revit.UI import *
from Autodesk.Revit.DB import *

level_name = "{level_name}"

try:
    # Collect all Level elements
    levels = FilteredElementCollector(doc).OfClass(Level).ToElements()
    found = False

    # Iterate over all Level elements to find the matching level
    for level in levels:
        if level.Name == level_name:
            result = {{
                "code": 200,
                "message": "Level found successfully",
                "level_id": level.Id.IntegerValue
            }}
            found = True
            break

    if not found:
        result = {{
            "code": 404,
            "message": "Level not found",
            "level_id": None
        }}

except Exception as e:
    result = {{
        "code": 500,
        "message": str(e),
        "level_id": None
    }}
"""
    return script


def create_wall_at_level(st_pt, ed_pt, layer_id):
    """
    创建墙
    :param
        st_pt(tuple): 墙的起点2D坐标 (x, y)。
        ed_pt(tuple): 墙的终点2D坐标 (x, y)。
        layer_id(int): 创建墙所在层的id。
    :return
        wall_id(int): 创建的墙的id
    """
    script = f"""import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
clr.AddReference('System')
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import *

t = Transaction(doc, "Create Wall")
layer_id = {layer_id}
try:
    # Find the level by the given ID
    layer_element = doc.GetElement(ElementId(layer_id))
    if not isinstance(layer_element, Level):
        result = {{
            "code": 400,
            "message": "The specified ID does not belong to a valid level."
        }}
    else:
        # Create XYZ coordinates for the wall's start and end points
        start_point = XYZ({st_pt[0]}, {st_pt[1]}, 0)
        end_point = XYZ({ed_pt[0]}, {ed_pt[1]}, 0)

        # Create a line for the wall
        wall_line = Line.CreateBound(start_point, end_point)

        # Default wall base and top elevations
        bottom_elevation = 0  # Height relative to the level's base
        top_elevation = 3000 / 304.8  # Convert 3000mm to feet (Revit uses feet by default)

        # Start a transaction to create the wall
        t.Start()

        # Create the wall
        new_wall = Wall.Create(doc, wall_line, layer_element.Id, False)

        # Set the wall's base and top heights
        base_offset_param = new_wall.get_Parameter(BuiltInParameter.WALL_BASE_OFFSET)
        base_offset_param.Set(bottom_elevation)

        top_offset_param = new_wall.get_Parameter(BuiltInParameter.WALL_HEIGHT_TYPE)
        unconnected_height_param = new_wall.get_Parameter(BuiltInParameter.WALL_USER_HEIGHT_PARAM)

        if top_offset_param.AsElementId() == ElementId.InvalidElementId:
            unconnected_height_param.Set(top_elevation)

        t.Commit()

        result = {{
            "code": 200,
            "message": "Wall created successfully",
            "wall_id": new_wall.Id.IntegerValue
        }}

except Exception as e:
    if t.HasStarted():
        t.RollBack()
    result = {{
        "code": 500,
        "message": str(e),
        "wall_id": None
    }}

"""
    return script


def add_door_to_wall(wall_id, door_family_name, door_level_id, door_location):
    """
    在墙上添加门
    :param
        wall_id(int): 要添加门的墙id
        door_family_name(string): 门的族名
        door_level_id(int): 门所在的标高id
        door_location(tuple): 门所在的2D坐标
    :return
        code(int): 状态代码
        message(str): 执行信息
        door_id(int): 创建的门id
    """
    script = f"""import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
clr.AddReference('System')
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import *
t = Transaction(doc, 'Add Door to Wall')
t.Start()

try:
    # Find the wall by the given wall_id
    wall = doc.GetElement(ElementId(int({wall_id})))
    if not wall or not isinstance(wall, Wall):
        result = {{
            'code': 400,
            'message': 'The specified wall ID does not belong to a valid wall.'
        }}
    else:
        # Find the door family by name
        door_family = None
        collector = FilteredElementCollector(doc).OfClass(Family)

        for element in collector:
            if element.Name == '{door_family_name}':
                door_family = element
                break

        if door_family is None:
            result = {{
                'code': 404,
                'message': 'The specified door family was not found.'
            }}
        else:
            # Ensure the door family type is active
            if not door_family.IsActive:
                door_family.Activate()
                doc.Regenerate()

            # Create the location point for the door
            door_point = XYZ({door_location[0]}, {door_location[1]}, 0)

            # Find the level by the given door_level_id
            door_level = doc.GetElement(ElementId(int({door_level_id})))
            if not isinstance(door_level, Level):
                result = {{
                    'code': 400,
                    'message': 'The specified level ID is not valid.'
                }}
            else:
                # Add the door to the wall
                new_door = doc.Create.NewFamilyInstance(door_point, door_family, wall, door_level, Structure.StructuralType.NonStructural)

                t.Commit()
                result = {{
                    'code': 200,
                    'message': 'Door added successfully',
                    'door_id': new_door.Id.IntegerValue
                }}
except Exception as e:
    if t.HasStarted():
        t.RollBack()
    result = {{
        'code': 500,
        'message': str(e),
        'door_id': None
    }}
"""
    return script


def add_window_to_wall(window_family_name, wall_id, x=0, y=0, base_offset=0):
    """
    Add a window to a specified wall.
    :param
        window_family_name (string): The name of the window family.
        wall_id (int): The ID of the wall to which the window will be added.
        x (float): The x-coordinate of the window's location.
        y (float): The y-coordinate of the window's location.
        base_offset (float): The offset of the window base from the wall's base level, in millimeters.
    :return
        script (string): RevitAPI script
    """
    script = f"""
import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
clr.AddReference('System')
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import *

# Retrieve the wall and window family symbol
wall = doc.GetElement(ElementId({wall_id}))
collector = FilteredElementCollector(doc).OfClass(FamilySymbol).ToElements()
window_symbol = None

t = Transaction(doc, 'Add Door to Wall')
t.Start()
for symbol in collector:
    if symbol.Family.Name == "{window_family_name}":
        window_symbol = symbol
        break

if window_symbol is None:
    result = {{
        "code": 500,
        "message": "Window family '{window_name}' not found.",
        "window_id": None
    }}
else:
    if not window_symbol.IsActive:
        window_symbol.Activate()
        doc.Regenerate()

    # Create the window's location point
    location_point = XYZ({x}, {y}, {base_offset} / 304.8)  # Convert mm to feet

    try:
        # Create the window instance
        window = doc.Create.NewFamilyInstance(location_point, window_symbol, wall, Structure.StructuralType.NonStructural)

        # Commit the transaction
        t.Commit()

        result = {{
            "code": 200,
            "message": "Window added successfully.",
            "window_id": window.Id.IntegerValue
        }}
    except Exception as e:
        if t.HasStarted():
            t.RollBack()
        result = {{
            "code": 500,
            "message": str(e),
            "window_id": None
        }}
"""
    return script


def get_all_level_ids():
    """
    检索所有的标高id
    :param

    :return
        code(int): 状态代码
        message(str): 执行信息
        level_ids(list): 所有的标高id
    """
    script = """import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
clr.AddReference("System")
from Autodesk.Revit.UI import *
from Autodesk.Revit.DB import *

try:
    # Collect all Level elements
    levels = FilteredElementCollector(doc).OfClass(Level).ToElements()

    # Gather all level IDs
    level_ids = [level.Id.IntegerValue for level in levels]

    if level_ids:
        result = {
            "code": 200,
            "message": "Level IDs retrieved successfully",
            "level_ids": level_ids
        }
    else:
        result = {
            "code": 404,
            "message": "No levels found",
            "level_ids": None
        }

except Exception as e:
    result = {
        "code": 500,
        "message": str(e),
        "level_ids": None
    }

"""
    return script


def get_family_instances():
    """
    获取所有的族实例
    :param

    :return
        code(int): 状态代码
        message(str): 执行信息
        family_instances(list): 族实例信息列表
    """
    script = """import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitServices')
from Autodesk.Revit.DB import *


# Collect all FamilyInstance elements
collector = FilteredElementCollector(doc).OfClass(FamilyInstance)

# List to store family instance information
family_instances = []

# Iterate over all family instances and extract their information
for fi in collector:
    family_name = fi.Symbol.Family.Name
    type_name = fi.Name
    instance_id = fi.Id.IntegerValue
    family_instances.append({
        "family_name": family_name,
        "type_name": type_name,
        "instance_id": instance_id
    })

# Prepare the result as a JSON response
result = {
    "code": 200,
    "message": "Family instances retrieved successfully",
    "family_instances": family_instances
}
"""
    return script


def get_families():
    """
    获取Revit文档中的所有族库
    :param

    :return
        code(int): 状态代码
        message(str): 执行信息
        families(list): 族库信息列表
    """
    script = """import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitServices')
from Autodesk.Revit.DB import *

# Collect all Family elements
collector = FilteredElementCollector(doc).OfClass(Family)

# List to store family information
families = []

# Iterate over all families and extract their information
for family in collector:
    family_name = family.Name
    family_id = family.Id.IntegerValue
    families.append({
        "family_name": family_name,
        "family_id": family_id
    })

# Prepare the result as a JSON response
result = {
    "code": 200,
    "message": "Families retrieved successfully",
    "families": families
}"""
    return script


# 后面增加roof类型参数
def add_roof_to_walls(wall_ids, roof_level_id):
    """
    在指定墙上创建屋顶
    :param
        wall_ids(list[int]): 墙的id列表
        roof_level_id(int): 屋顶所在的标高id
    :return
        code(int): 状态代码
        message(str): 执行信息
        roof_id(int): 创建的屋顶id
    """
    script = f"""import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
clr.AddReference('System')
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import *
t = Transaction(doc, "Add Roof to Walls")

try:
    # Find the walls by the given wall_ids
    walls = [doc.GetElement(ElementId(int(wall_id))) for wall_id in {wall_ids}]
    if any(not wall or not isinstance(wall, Wall) for wall in walls):
        result = {{
            "code": 400,
            "message": "One or more specified wall IDs do not belong to valid walls."
        }}
    else:
        # Get the roof level
        roof_level = doc.GetElement(ElementId(int({roof_level_id})))
        if not isinstance(roof_level, Level):
            result = {{
                "code": 400,
                "message": "The specified roof level ID is not valid."
            }}
        else:
            # Start the transaction
            t.Start()

            # Create a curve array for the roof profile
            curve_array = CurveArray()
            for wall in walls:
                wall_curve = wall.Location.Curve
                curve_array.Append(wall_curve)

            # Define the roof type
            roof_type = FilteredElementCollector(doc).OfClass(RoofType).FirstElement()

            if roof_type is None:
                result = {{
                    "code": 404,
                    "message": "No valid roof type found."
                }}
            else:
                # Create the roof
                new_roof = doc.Create.NewFootPrintRoof(curve_array, roof_level, roof_type, None)

                # Commit the transaction
                t.Commit()

                result = {{
                    "code": 200,
                    "message": "Roof added successfully",
                    "roof_id": new_roof.Id.IntegerValue
                }}

except Exception as e:
    if t.HasStarted():
        t.RollBack()
    result = {{
        "code": 500,
        "message": str(e),
        "roof_id": None
    }}
"""
    return script


# 后面增加floor类型参数
def add_floor_at_level(boundary_points, floor_level_id):
    """
    在指定标高创建一个地板
    :param
        boundary_points(list[tuple[float, float]]): 地板边界点的坐标列表 [(x1, y1), (x2, y2), ...]
        floor_level_id(int): 地板所在的标高id
    :return
        code(int): 状态代码
        message(str): 执行信息
        floor_id(int): 创建的地板id
    """
    script = f"""import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
clr.AddReference('System')
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import *
from System.Collections.Generic import List

t = Transaction(doc, "Add Floor at Level")

try:
    # Convert boundary points to XYZ points
    boundary_points = {boundary_points}
    if len(boundary_points) < 3:
        result = {{
            "code": 400,
            "message": "At least three boundary points are required to define a floor."
        }}
    else:
        # Convert boundary points to CurveArray
        curve_array = CurveArray()
        for i in range(len(boundary_points)):
            pt1 = XYZ(*boundary_points[i])
            pt2 = XYZ(*boundary_points[(i + 1) % len(boundary_points)])
            curve = Line.CreateBound(pt1, pt2)
            curve_array.Append(curve)

        # Get the floor level
        floor_level = doc.GetElement(ElementId(int({floor_level_id})))
        if not isinstance(floor_level, Level):
            result = {{
                "code": 400,
                "message": "The specified floor level ID is not valid."
            }}
        else:
            # Start the transaction
            t.Start()

            # Define the floor type
            floor_type = FilteredElementCollector(doc).OfClass(FloorType).FirstElement()

            if floor_type is None:
                result = {{
                    "code": 404,
                    "message": "No valid floor type found."
                }}
            else:
                # Create the floor
                new_floor = doc.Create.NewFloor(curve_array, floor_type, floor_level, False)

                # Commit the transaction
                t.Commit()

                result = {{
                    "code": 200,
                    "message": "Floor added successfully",
                    "floor_id": new_floor.Id.IntegerValue
                }}

except Exception as e:
    if t.HasStarted():
        t.RollBack()
    result = {{
        "code": 500,
        "message": str(e),
        "floor_id": None
    }}

print(result)
"""
    return script
