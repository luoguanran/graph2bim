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
        question = "找到10个系统中命名不规范的项目名称，并分析其原因"
        print("问题：" + question)
        prompt_text2sql = '''角色：现在你是一个资深的数据库需求分析人员
        问题：{}
        请将该问题转化为SQL语句，以;结尾。生成的字段只能从下面的表中寻找，此外如果该问题包含多个子问题，则将其转化为多个SQL语句。
        下面是提供的表的信息：
        模型目录表：pm_bim_catalog
        参数名	描述
        id	id
        parent_id	父节点ID
        inner_code	树形层级码
        is_leaf	是否叶子节点
        order_no	排序号
        update_date	更新时间
        update_by	更新者ID
        update_by_name	更新者名称
        create_date	创建时间
        create_by	创建者ID
        create_by_name	创建者名称
        catalog_name	名称
        is_root	授权目录（0-否，1-是）
        is_ext	是否扩展目录（0-否，1-是）
        is_nouse	是否禁用（0-否，1-是）
        remarks	备注

        模型目录关联模型表：pm_bim_catalog_model
        参数名	描述
        id	id
        catalog_id	模型目录id
        model_id	模型id

        模型信息表：pm_bim_data_sync
        参数名	描述
        id	id
        project_id	项目id
        project_name	项目名称
        construction_name	工程名称
        construction_longitude	工程经度
        construction_latitude	工程纬度
        bim_file_id	BIM模型文件ID
        bim_file_name	BIM模型文件名称
        bim_file_size	BIM模型文件大小
        bim_file_create_time	BIM模型文件创建时间
        bim_data_folder	BIM数据包文件夹
        sync_status	同步状态标识(00:初始状态;10:模型文件已上传;20:模型文件已转换;30:数据包已同步;40:项目已挂接)
        sync_status_name	同步状态
        sync_time_stamp	同步时间戳
        remarks	备注
        main_flag	主模型标记
        del_flag	删除标记
        create_by	创建者id
        create_by_name	创建者名称
        create_date	创建时间
        update_by	更新者id
        update_date	更新时间
        app_key	appkey
        is_integrate	是否集成
        bim_file_ids	BIM模型文件IDs
        translating	是否转换中(0-否，1-是)
        load_mode	加载模式(0-流式加载/1-全量加载)
        project_overview	工程概况
        is_ar	是否需要AR集成(0-无; 1-已提交AR集成; 2-已完成集成; )
        component_num	构件数量'''.format(question)
        completion_text2sql = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
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

        # 执行查询语句
        sql_search_result = []
        result_set_number = 1
        for sql_statement in sql_list:
            cursor.execute(sql_statement)
            result = str(cursor.fetchall())
            sql_search_result.append(f"sql查询结果{result_set_number}:" + result)
            result_set_number += 1
        print(sql_search_result)

        prompt_sql2text = "根据sql的查询结果回答问题：{}".format(question)
        # print(prompt_sql2text)
        completion_sql2text = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": prompt_text2sql},
                {"role": "assistant", "content": str(sql_search_result)},
                {"role": "user", "content": prompt_sql2text}
            ]
        )
        answer = completion_sql2text.choices[0].message.content
        print(answer)
finally:
    conn.close()

