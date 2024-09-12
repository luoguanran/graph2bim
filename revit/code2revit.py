import json

import requests
import openai
from BIMagent import *

openai.api_key = 'sk-ogHsmNlcbHP7W13X1ZpGrUms7z7JEmfqhzJw7LDr6tCNHUit'

tool_library = '''
        # create_level(elevation, level_name="")
        创建标高
        :param
            level_name(str): 标高平面的名称，默认为空
            elevation(float): 高程，单位为mm
        :return
            code(int): 状态代码
            message(str): 执行信息
            level_id(int): 创建的标高id
    
        # create_column(base_level_id, top_level_id, location_point)
        创建结构柱
        :param
            base_level_id(int): 基准标高的ID
            top_level_id(int): 顶部标高的ID
            location_point(tuple): 结构柱的位置点，格式为(x, y)
        :return
            code(int): 状态代码
            message(str): 执行信息
            column_id(int): 创建的结构柱id
    
        # delete_element(element, is_element_type=False)
        删除指定元素实例或类型
        :param
            element(str): BuiltInCategory枚举类，如'OST_Roofs'
            is_element_type(bool): 删除的元素是否为类型，默认为False
        :return
            code(int): 状态代码
            message(str): 执行信息
            deleted_ids(list): 删除的元素id
    
        # select_element(element, is_element_type=False):
        搜索指定元素实例或类型
        :param
            element(str): BuiltInCategory枚举类，如'OST_Roofs'
            is_element_type(bool): 删除的元素是否为类型，默认为False
        :return
            code(int): 状态代码
            message(str): 执行信息
            element_ids(list): 搜索的元素id
    
    
        # get_level_by_name(level_name)
        根据标高的名称获取ID
        :param
            level_name(str): 标高/层高的名称。
        :return
            element_id(int): 标高ID，如果未找到则返回None。
    
        # create_wall_at_level(st_pt, ed_pt, layer_id)
        创建墙，需要先创建所在的标高
        :param
            st_pt(tuple): 墙的起点2D坐标 (x, y)。
            ed_pt(tuple): 墙的终点2D坐标 (x, y)。
            layer_id(int): 创建墙所在层的id。
        :return
            wall_id(int): 创建的墙的id
            
        # get_all_level_ids()
        检索所有的标高id
        :param
    
        :return
            code(int): 状态代码
            message(str): 执行信息
            door_id(int): 创建的门id
            
        # add_door_to_wall(wall_id, door_family_name, door_level_id, door_location)
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
        
        # get_family_instances()
        获取所有的族实例
        :param
        
        :return
            code(int): 状态代码
            message(str): 执行信息
            family_instances(list): 族实例信息列表
            
        # get_families()
        获取所有的族库
        :param
        
        :return
            code(int): 状态代码
            message(str): 执行信息
            families(list): 族库信息列表
            
        # add_window_to_wall(window_family_name, wall_id, x=0, y=0, base_offset=0)
        在墙上添加窗
        :param
            window_family_name(string): 窗的族名
            wall_id(int): 要添加窗的墙id
            x(float): 窗的x坐标
            y(float): 窗的z坐标
            base_offset(float): 窗底距墙底标高的偏移量，单位为mm
        :return
            code(int): 状态代码
            message(str): 执行信息
            window_id(int): 创建的窗id
        
        # add_roof_to_walls(wall_ids, roof_level_id)
        在指定墙上创建屋顶
        :param
            wall_ids(list[int]): 墙的id列表
            roof_level_id(int): 屋顶所在的标高id
        :return
            code(int): 状态代码
            message(str): 执行信息
            roof_id(int): 创建的屋顶id
            
        # add_floor_at_level(boundary_points, floor_level_id)
        在指定标高创建一个地板
        :param
            boundary_points(list[tuple[float, float]]): 地板边界点的坐标列表 [(x1, y1), (x2, y2), ...]
            floor_level_id(int): 地板所在的标高id
        :return
            code(int): 状态代码
            message(str): 执行信息
            floor_id(int): 创建的地板id
'''

func_dict = {
    "create_level": "create_level(elevation, level_name='')",
    "create_grid": "create_grid(start_point, end_point, grid_name='')",
    "create_column": "create_column(base_level_id, top_level_id, location_point)",
    "delete_element": "delete_element(element, is_element_type=False)",
    "select_element": "select_element(element, is_element_type=False)",
    "get_level_by_name": "get_level_by_name(level_name)",
    "create_wall_at_level": "create_wall_at_level(st_pt, ed_pt, layer_id)",
    "get_all_level_ids": "get_all_level_ids()",
    "add_door_to_wall": "add_door_to_wall(wall_id, door_family_name, door_level_id, door_location)",
    "get_family_instances": "get_family_instances()",
    "get_families": "get_families()",
    "add_window_to_wall": "add_window_to_wall(window_family_name, wall_id, x=0, y=0, base_offset=0)",
    "add_roof_to_walls": "add_roof_to_walls(wall_ids, roof_level_id)",
    "add_floor_at_level": "add_floor_at_level(boundary_points, floor_level_id)"
}

func_dict1 = {
    "create_level": "create_level(elevation, level_name='') | level_name(str): 标高平面的名称，默认为空; elevation(float): 高程，单位为mm",
    "create_grid": "create_grid(start_point, end_point, grid_name='') | grid_name(string): 轴网的名称，默认为空;start_point(array): 起点坐标(x, y, z);end_point(array): 终点坐标(x, y, z)",
    "create_column": "create_column(base_level_id, top_level_id, location_point, width, height) | base_level_id(int): 基准标高的ID; top_level_id(int): 顶部标高的ID; location_point(tuple): 结构柱的位置点，格式为(x, y); width(float): 可选，结构柱的宽度，单位为mm; height(float): 可选，结构柱的高度，单位为mm",
    "delete_element": "delete_element(element, is_element_type=False) | element(str): BuiltInCategory枚举类，如'OST_Roofs'; is_element_type(bool): 删除的元素是否为类型，默认为False",
    "select_element": "select_element(element, is_element_type=False) | element(str): BuiltInCategory枚举类，如'OST_Roofs'; is_element_type(bool): 删除的元素是否为类型，默认为False",
    "get_level_by_name": "get_level_by_name(level_name) | level_name(str): 标高/层高的名称",
    "create_wall": "create_wall(st_pt, ed_pt, layer_id) | st_pt(tuple): 墙的起点2D坐标 (x, y); ed_pt(tuple): 墙的终点2D坐标 (x, y); layer_id(int): 创建墙所在层的id",
    "get_all_level_ids": "get_all_level_ids()",
    "add_door_to_wall": "add_door_to_wall(wall_id, door_family_name, door_level_id, door_location) | wall_id(int): 要添加门的墙id; door_family_name(string): 门的族名; door_level_id(int): 门所在的标高id; door_location(tuple): 门所在的2D坐标",
    "get_family_instances": "get_family_instances()",
    "get_families": "get_families()",
    "add_window_to_wall": "add_window_to_wall(window_name, wall_id, x=0, y=0, base_offset=0) | window_name(string): 窗的族名; wall_id(int): 要添加窗的墙id; x(float): 窗的x坐标; y(float): 窗的z坐标; base_offset(float): 窗底距墙底标高的偏移量，单位为mm",
    "add_roof_to_walls": "add_roof_to_walls(wall_ids, roof_level_id) | wall_ids(list[int]): 墙的id列表; roof_level_id(int): 屋顶所在的标高id",
    "add_floor_at_level": "add_floor_at_level(boundary_points, floor_level_id) | boundary_points(list[tuple[float, float]]): 地板边界点的坐标列表 [(x1, y1), (x2, y2), ...]; floor_level_id(int): 地板所在的标高id"
}


def get_generated_design(task):
    architect_agent = f'''你是一位经验丰富的建筑师，可以根据用户的需求设计楼层/建筑平面图。您将利用您丰富的架构知识来扩展和补充用户的原始描述，并最终以结构化文本格式表达您的设计。根据用户的具体需求，尝试在输出中包括每面墙的起点和终点、门窗的位置（相对于墙的起点偏移）、内部房间/功能区的边界以及完整建筑所需的其他组件的位置和几何细节。
        #请参考基本的建筑规则，如：
        -基础：确保坚实的基础板可以支撑整个结构。墙板和屋顶的设计必须使重量均匀地分布在基础上
        -墙体配置：布置墙体以确定建筑物的周边和内部空间。确保承重墙的间距和位置足够，以均匀分配结构的重量。为每层楼正确设置墙标高。
        -楼板设计：为每层楼铺设楼板。它们应该是水平的，由墙壁支撑，提供稳定性并分隔不同的楼层
        -门的位置：将门放置在便于进入不同房间和区域的位置。建筑的主入口应突出且易于定位，内部门应便于平稳移动
        -室内布局：合理组织和定义室内布局。使用内墙分隔不同功能的房间，并通过适当放置的门确保它们之间的流通结构完整性：确保所有构件（墙、板、屋顶）连接牢固且稳定。
        -合规性：避免建筑构件发生冲突/重叠，例如不同区域之间的重叠隔墙和重叠的门窗位置。相邻的房间可以共享内部隔墙。房间还可以利用外墙。
        #使你的设计在空间和几何上合理。使用mm为单位。尽量减少其他无关文本。
        #这是一个示例对话：
        用户：我想建一栋办公楼。我希望这座建筑有3层，每层的布局都是一样的。每层楼有6个房间，每侧3个，由3米宽的走廊隔开。每个房间都有一扇门和一扇窗户。每个房间的门应位于走廊一侧的墙上，窗户应位于建筑物的外墙上
        -建筑师：**3-Floor Office Building Design** 
        **Foundation** 
        - Rectangular foundation slab: 30000mm x 15000mm 
        **Ground Floor Plan:** 
        1. **Perimeter Walls:** 
        - Wall A: (0,0) to (30000,0) 
        - Wall B: (30000,0) to (30000,15000) 
        - Wall C: (30000,15000) to (0,15000) 
        - Wall D: (0,15000) to (0,0) 
        2. **Functional Areas** 
        Boundary in format (x_min,y_min), (x_max,y_max): 
        - Room 1: (0,0), (10000,6000) 
        - Room 2: (10000,0), (20000,6000) 
        - Room 3: (20000,0), (30000,6000) 
        - Room 4: (0,9000), (10000,15000) 
        - Room 5: (10000,9000), (20000,15000) 
        - Room 6: (20000,9000), (30000,15000) 
        - Central corridor: (0,6000), (30000,9000) 
        3. **Internal Corridor Walls:** 
        - Wall E: (0,6000) to (30000,6000) 
        - Wall F: (0,9000) to (30000,9000) 
        4. **Room Dividing Walls:** 
        - Wall G: (10000,0) to (10000,6000) 
        - Wall H: (20000,0) to (20000,6000) 
        - Wall I: (10000,9000) to (10000,15000) 
        - Wall J: (20000,9000) to (20000,15000) 
        5.**Doors:** 
        Insertion offset of each room door relative to the start of the corresponding wall: 
        -Room 1 door on corridor wall E: 5000 
        - Room 2 door on corridor wall E: 15000 
        - Room 3 door on corridor wall E: 25000 
        - Room 4 door on corridor wall F: 5000 
        - Room 5 door on corridor wall F: 15000 
        - Room 6 door on corridor wall F: 25000 
        6.**Windows:** 
        Insertion offset of each room window relative to the start of the corresponding wall: 
        - Room 1 window on wall A: 5000 
        - Room 2 window on wall A: 15000 
        - Room 3 window on wall A: 25000 
        - Room 4 window on wall C: 5000 
        - Room 5 window on wall C: 15000 
        - Room 6 window on wall C: 25000 
        **First Floor Plan:** - 
        Identical to Ground Floor Plan 
        **Second Floor Plan:** 
        - Identical to Ground Floor Plan
        **Roof Construction:** 
        - Roof covering entire building: (0,0) to (3000,0) to 30000,15000) to (0,15000) to (0,0). 
        **Slab Design:** 
        - Create slabs for each floor supported by perimeter and internal walls. Slabs covering entire floor area with same dimensions as foundation. 
        **Summary:** 
        - Building dimensions: 30000mm x 15000mm x 3 floors. 
        - Each floor has 6 rooms, 3 on each side of a central corridor. 
        The user now provides the following instruction, please generate the plan as an architect. Let's think step by step.
    用户：{task}
    建筑师：'''
    response = chat(architect_agent)
    architect_agent_history = f'''
    用户：{task}
    建筑师：{response}'''
    return response, architect_agent_history


def get_generated_product(task):
    productor_agent = f'''您是一位经验丰富的产品开发人员，可以指导AI程序员调用python脚本来完成建筑师指定的任务。您精通理解RevitAPI文档，能够根据可用功能将建筑师的原始指令分解为子任务和子逻辑，并能够以更严格和详细的方式表达建筑师的描述。在指导程序员时，请详细说明坐标和尺寸。当您觉得需要建筑师设计计划或更多建筑背景来协助您的指示时，请咨询建筑师。如果设计方案中给出了功能区域，请务必指导程序员创建它们。您必须参考架构知识，以确保您的内容在空间和几何上都是合理的。使用mm为单位。一步一步地思考。尽量减少其他无关文本。作为参考，以下是程序员可用的API函数，请尝试给出如何有效使用它们的提示：
        ***工具库***
        {tool_library}
    现在，根据下面给出的对话，请转达建筑师的指示，并选择调用的函数，如果缺少对应的函数则补充该函数的功能和说明。你不需要写代码，只需要一步一步地指导程序员如何调用和补充函数。
    建筑师：{task}
    产品负责人：'''
    response = chat(productor_agent)
    productor_agent_history = f'''
    用户：{task}
    产品负责人：{response}'''
    return response, productor_agent_history


def get_generated_code(task):
    coder_agent = f'''你是一名AI程序员。您的工作是选择调用合适的工具函数来实现建筑师的要求。只需要输出调用的函数，并根据建筑师的规划确定参数即可，不需要其它任何内容。您应该避免在代码中假设变量是预定义的。
        ***工具库***
        {tool_library}
    代码中只使用你可以使用的工具函数，而不是试图发明新的工具。使用mm单位。现在，请根据下面的对话，以程序员的身份选择调用函数。注意如果有当前不确定的参数，不要嵌套调用函数，而应该用"unknown"填充：
    建筑师： {task}
    程序员：'''
    response = chat(coder_agent)
    coder_agent_history = f'''
    用户：{task}
    程序员：{response}'''
    return response, coder_agent_history


def chat(task):
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": task}
        ]
    )
    response = completion.choices[0].message.content
    return response


def format_code(input_code):
    formatted_code = []
    for line in input_code.split('\n'):
        if line and "doc =" not in line and 'app =' not in line and 'uiapp =' not in line:
            formatted_code.append(line)
    return '\n'.join(formatted_code)


def send_code_to_revit(input_code):
    api_url = "http://localhost:5000/execute_revit_code"
    # return_code = format_code(input_code)
    # print("生成代码：" + input_code)
    headers = {
        'Content-Type': 'text/plain; charset=utf-8'  # 设置请求头以使用 UTF-8 编码
    }
    response = requests.post(api_url, data=input_code.encode('utf-8'), headers=headers)
    return response.text


if __name__ == "__main__":
    # 创建一个10×6米四层住宅的基本三维模型

    # 文档中所有族-族类型
    families = send_code_to_revit(get_families())
    families_info = json.loads(families)['families']
    print("------families info------")
    print(families_info)
    description = input("请输入你的需求：")
    history = []
    architect_design, architect_history = get_generated_design(description)
    history.append(architect_history)
    print("--------------")
    print(architect_design)
    call_tools, code_history = get_generated_code(architect_design)
    history.append(code_history)
    print("--------------")
    print(call_tools)
    call_tool_list = call_tools.strip().split('\n')
    # 过滤掉空行
    call_tool_list = [line for line in call_tool_list if line.strip()]
    call_func_history = []
    for tool in call_tool_list:
        func_name = tool.split("(")[0]
        func_description = func_dict[func_name]
        caller_agent = ""
        if "family_name" in func_description:
            caller_agent = f'''
            history: {call_func_history}
            all_family_info: {families_info}
            call_func: {tool}
            func_description: {func_description}
            请检查上面的call_func，将"unknown"参数用history中的结果进行代替，并在all_family_info中搜索可用的family_name代替原来对应的参数。
            checked_func:'''
        else:
            caller_agent = f'''
            history: {call_func_history}
            call_func: {tool}
            func_description: {func_description}
            请检查上面的call_func，将"unknown"参数用history中的结果进行代替。
            checked_func:'''
        checked_tool = chat(caller_agent)
        print(checked_tool)
        script = eval(checked_tool)
        result = send_code_to_revit(script)
        # 增加异常处理程序
        # result_dict = json.loads(result)
        # code = result_dict['code']
        # if code == 500:
        #     # 正常执行
        # else:
        #     # reviwer_agent
        #
        #     # 使用LLM检查，并更正参数
        call_func_history.append(f"func:{checked_tool}, result:{result}")
        print(result)

    # system = f'''你现在是一个BIM智能体，请根据用户的需求，从下面库中选择调用相应的函数，需要遵循以下要求：
    # 1.将用户需求中的参数单位转化为调用函数的参数单位
    # 2.只输出调用函数，不要出现任何注释说明
    # 用户需求：{description}
    # ***工具库***
    # {tool_library}
    # '''

    # # 生成调用函数
    # call_func = chat(system)
    # print(call_func)
    # script = eval(call_func)
    # result = send_code_to_revit(script)
    # print("result:"+result)
