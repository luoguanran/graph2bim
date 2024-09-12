import openai
import pymysql
import re
openai.api_key = 'sk-ogHsmNlcbHP7W13X1ZpGrUms7z7JEmfqhzJw7LDr6tCNHUit'

# 建立数据库连接
conn = pymysql.connect(host='localhost',
                       port=3306, user='root',
                       password='8831651',
                       db='bim',
                       client_flag=pymysql.constants.CLIENT.MULTI_STATEMENTS)


try:
    with conn.cursor() as cursor:
        question = "Propose an exterior wall detail for a housing project located in Poissy, France. The finishing must be durable, white-colored material for the exterior, and light-colored wooden material for the interior."
        print("QUESTION：" + question)
        classify_prompt = '''Input (Task prompt): {}
        Instruction prompt: Return in JSON format with the properties 'activity type', 'component type', and 'level' with integer values corresponding to the following descriptions. If the objective is unclear, ask for clarification:
        'activity_type':
        1 = Generate (i.e., create, propose, suggest),
        2 = Modify (i.e., change, replace),
        3 = Retrieve (i.e., return, show),
        4 = Delete (i.e., remove).
        'component_type':
        1 = Wall, 2 = Window, ...
        'level':
        1 = Detail class (i.e., detail, type),
        2 = Object (i.e., instance, element).'''.format(question)
        completion_classify = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": classify_prompt}
            ]
        )
        task_type = completion_classify.choices[0].message.content
        print(task_type)

        # 根据task_type分配不同的prompt
        wall_detail_prompt = '''Input (Task prompt): {}
        Instruction prompt: Return in JSON format with 'wall_detail_name' and each layer with 'material', 'layer_type', 'thermal_conductivity' (W/m·K), and 'thickness' (mm), with exact values without units, and in order of exterior to interior layer.'''.format(question)

        completion_wall = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": wall_detail_prompt}
            ]
        )
        class_detail = completion_wall.choices[0].message.content
        print(class_detail)
finally:
    conn.close()

