from datetime import datetime
import json
import requests


class Coordinates:
    def __init__(self, long: float, lat: float) -> None:
        self.long = long
        self.lat = lat


class Item:
    def __init__(
        self,
        sn_nema: str,
        insertion_date: datetime,
        coordinates: Coordinates,
        picture: str,
        picture_raw_data: bytes,
        notes: str,
        old_sn: str,
        lamp_type: str,
        type_switch: str,
        _id: str = None,
    ) -> None:
        self.sn = sn_nema
        self.date = insertion_date
        self.address = coordinates
        self.picture = picture
        self.picture_raw_data = picture_raw_data
        self.notes = notes
        self.old_sn = old_sn
        self.lamp_type = lamp_type
        self.type_switch = type_switch
        self.id = _id


class MondayClient:
    def __init__(self, api_key: str) -> None:
        self.api_key = api_key
        self._base_url = 'https://api.monday.com/v2'
        self._headers = {
            'Authorization': self.api_key,
        }

    def _query(self, query):
        return requests.post(
            url=self._base_url,
            headers=self._headers,
            json={
                'query': query,
            }
        ).json()

    def add_item(
        self,
        board_id: int,
        group_id: str,
        item: Item,
    ) -> str:
        formatted_date = item.date.strftime('%Y-%m-%d')
        formatted_status = 'לא ידוע' if not item.lamp_type else item.lamp_type
        formatted_type_switch = '' if not item.type_switch else item.type_switch
        payload = f'''
            mutation {{
                create_item(
                    board_id: {board_id},
                    group_id: "{group_id}",
                    item_name: "{item.sn}",
                    create_labels_if_missing: true,
                    column_values: "{{
                        \\"text4\\": \\"{item.notes}\\",
                        \\"location\\": {{
                            \\"lat\\": \\"{item.address.lat}\\",
                            \\"lng\\":\\"{item.address.long}\\",
                            \\"address\\":\\"{item.sn}\\"
                        }},
                        \\"date4\\" : {{ 
                            \\"date\\": \\"{formatted_date}\\"
                        }},
                        \\"text7\\": \\"{item.old_sn}\\",
                        \\"label3\\": {{
                             \\"label\\": \\"{formatted_status}\\"
                        }},
                        \\"status_1\\": {{
                             \\"label\\": \\"{formatted_type_switch}\\"
                        }}

                    }}"
                ) 
                {{
                    id
                }}
            }}'''

        return self._query(query=payload)['data']['create_item']['id']

    def add_item_picture(
        self,
        item_id: str,
        image_raw_data: bytes,
    ) -> None:
        payload = {
            'query': 'mutation ($file: File!) { add_file_to_column (file: $file, item_id: ' + item_id + ', column_id: "files") {id }}'
        }

        files = [
            (
                'variables[file]', (
                    'filename',
                    image_raw_data,
                    'contenttype',
                )
            )
        ]
        headers = {
            'Authorization': self.api_key,
        }
        response = requests.post(
            self._base_url,
            headers=headers,
            data=payload,
            files=files
        )

    def update_item(self, board_id: int, new_item: Item):
        formatted_date = new_item.date.strftime('%Y-%m-%d')
        formatted_status = 'לא ידוע' if not new_item.lamp_type else new_item.lamp_type
        formatted_type_switch = '' if not new_item.type_switch else new_item.type_switch
        update_query = f''' mutation {{
                        change_multiple_column_values (
                            board_id: {board_id}
                            item_id: {new_item.id}
                                column_values: "{{
                                    \\"text4\\": \\"{new_item.notes}\\",
                                    \\"location\\": {{
                                        \\"lat\\": \\"{new_item.address.lat}\\",
                                        \\"lng\\": \\"{new_item.address.long}\\",
                                        \\"address\\": \\"{new_item.sn}\\"
                                                }}, 
                                            \\"date4\\" : {{
                                    \\"date\\": \\"{formatted_date}\\"
                                    }},
                                            \\"text7\\": \\"{new_item.old_sn}\\",
                                                \\"label3\\": {{
                                    \\"label\\": \\"{formatted_status}\\"
                                    }},
                                            \\"status_1\\": {{
                                    \\"label\\": \\"{formatted_type_switch}\\"
                                    }}
                                            
                                    }}"
                                ) 
                            {{
                                id
                            }} 
                        }}'''
        self._query(update_query)

    