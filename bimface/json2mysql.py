import requests
import pymysql

class BIMFaceAPI:
    def __init__(self, db_config, access_token_url, access_token_header):
        self.db_config = db_config
        self.access_token_url = access_token_url
        self.access_token_header = access_token_header
        self.access_token = self.get_access_token()
        self.conn = pymysql.connect(**db_config)
        self.cursor = self.conn.cursor()

    def get_access_token(self):
        response = requests.post(self.access_token_url, headers=self.access_token_header)
        if response.status_code == 200:
            print('Request was successful!')
            json_data = response.json()
            return json_data['data']['token']
        else:
            print(f'Error: {response.status_code}')
            return None

    def get_model_info(self, file_id):
        url_request_model_info = f'https://api.bimface.com/data/v2/files/{file_id}/elementIds'
        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = requests.get(url_request_model_info, headers=headers)

        if response.status_code == 200:
            print('Request was successful!')
            json_data = response.json()
            return json_data['data']
        else:
            print(f'Error: {response.status_code}')
            return None

    def get_element_info(self, file_id, element_id):
        url_request_element_info = f'https://api.bimface.com/data/v2/files/{file_id}/elements/{element_id}'
        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = requests.get(url_request_element_info, headers=headers)

        if response.status_code == 200:
            print('Request was successful!')
            json_data = response.json()
            return json_data['data']
        else:
            print(f'Error: {response.status_code}')
            return None

    def create_model_table(self, file_id):
        table_name = f"model_{file_id}"
        self.cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS {table_name} (
            elementId VARCHAR(255) PRIMARY KEY,
            familyGuid VARCHAR(255),
            guid VARCHAR(255),
            name VARCHAR(255)
        )
        ''')
        self.cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS properties (
            elementId VARCHAR(255),
            group_name VARCHAR(255),
            item_key VARCHAR(255),
            item_value TEXT,
            unit VARCHAR(50),
            valueType INT
        )
        ''')
        return table_name

    def insert_element(self, table_name, element_info):
        element = (
            element_info['elementId'],
            element_info['familyGuid'],
            element_info['guid'],
            element_info['name']
        )
        self.cursor.execute(f'''
        INSERT IGNORE INTO {table_name} (elementId, familyGuid, guid, name) 
        VALUES (%s, %s, %s, %s)
        ''', element)

    def insert_properties(self, properties_table_name, element_info):
        for group in element_info['properties']:
            group_name = group['group']
            for item in group['items']:
                property_item = (
                    element_info['elementId'],
                    group_name,
                    item['key'],
                    item['value'],
                    item.get('unit', ''),
                    item.get('valueType', 0)
                )
                print(property_item)
                self.cursor.execute(f'''
                INSERT IGNORE INTO {properties_table_name} (elementId, group_name, item_key, item_value, unit, valueType) 
                VALUES (%s, %s, %s, %s, %s, %s)
                ''', property_item)

    def process_file(self, file_id):
        element_id_list = self.get_model_info(file_id)
        model_table_name = self.create_model_table(file_id)
        for element_id in element_id_list:
            element_info = self.get_element_info(file_id, element_id)
            self.insert_element(model_table_name, element_info)
            self.insert_properties("properties", element_info)
        self.conn.commit()

    def close_connection(self):
        self.conn.close()

if __name__ == '__main__':
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
    bimface_api.process_file(file_id)
    bimface_api.close_connection()
