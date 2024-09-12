import openai
import pymysql
import re
from json2mysql import BIMFaceAPI
openai.api_key = 'sk-ogHsmNlcbHP7W13X1ZpGrUms7z7JEmfqhzJw7LDr6tCNHUit'

#
db_config = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '8831651',
    'db': 'bim',
    'client_flag': pymysql.constants.CLIENT.MULTI_STATEMENTS
}
access_token_url = 'https://api.bimface.com/oauth2/token'
access_token_header = {
    'Authorization': 'Basic ZlcyWkp1WU5RUzRZT3gwaDQ2WG1nb2ZBUFk2YTJIUUY6RmxoSk9oZUpHMmtaQXNmUm1RdlJGcHhwblc2SjgybVM='
}
file_id = '10000862377193'

bimface_api = BIMFaceAPI(db_config, access_token_url, access_token_header)
# bimface_api.process_file(file_id)
bimface_api.close_connection()

# 建立数据库连接
conn = pymysql.connect(host='localhost',
                       port=3306, user='root',
                       password='8831651',
                       db='bim',
                       client_flag=pymysql.constants.CLIENT.MULTI_STATEMENTS)

try:
    with conn.cursor() as cursor:
        question = "分析模型中命名不规范的构件"
        print("问题："+question)
        prompt_text2sql = f'''角色：现在你是一个资深的数据库需求分析人员
        问题：{question}
        请一步一步思考，将该问题转化为SQL语句，以;结尾。如果该问题包含多个子问题，则将其转化为多个SQL语句。
        下面是提供的表的信息：
        构件目录表：model_{file_id}
        参数名	描述
        elementId	构件id
        familyGuid	构件所属家族的全局id
        guid	构件的全局id
        name	构件名称

        构件信息表：properties
        参数名	描述
        elementId	构件id
        group_name	属性组的名称
        item_key	属性项的键
        item_value	属性项的值
        unit	属性值的单位(如果没有单位则为空字符串)
        valueType	属性值的类型(如果没有类型则为0)'''
        completion_text2sql = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "user", "content": prompt_text2sql}
            ]
        )
        sql_text = completion_text2sql.choices[0].message.content
        # print(sql_text)

        # 处理返回的sql语句，确保能够执行
        pattern = r'SELECT.*?;'
        sql_list = re.findall(pattern, sql_text, re.DOTALL | re.IGNORECASE)
        sql_list = [sql.strip() for sql in sql_list]
        print(sql_list)

        # 执行查询语句
        sql_search_result = []
        result_set_number = 1
        for sql_statement in sql_list:
            cursor.execute(sql_statement)
            result = str(cursor.fetchall())
            sql_search_result.append(f"sql查询结果{result_set_number}:" + result)
            result_set_number += 1
        # print("查询结果："+str(sql_search_result))

        prompt_sql2text = "根据sql的查询结果回答问题，如果为空则提示没有找到相关数据：{}".format(question)
        # print(prompt_sql2text)
        completion_sql2text = openai.ChatCompletion.create(
            model="gpt-4-32k",
            messages=[
                {"role": "user", "content": prompt_text2sql},
                {"role": "assistant", "content": str(sql_search_result)},
                {"role": "user", "content": prompt_sql2text}
            ]
        )
        answer = completion_sql2text.choices[0].message.content
        print("回答："+answer)
finally:
    conn.close()

