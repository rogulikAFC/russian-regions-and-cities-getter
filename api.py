import ast
import requests


class Api:
    """
    Класс умеет запрашивать у http api информацию о регионах России, форматировать эту информацию в вид [{'region_name': 'region_iso'},] и записывать информацию.
    Пути для записи информации заданы в конструкторе класса.
    """

    def __init__(self, format: str, api_key: str, balance: int):
        self.api_key = api_key

        self.cities_request_url = 'http://htmlweb.ru/geo/api.php?area={region_num}&json&api_key={api_key}&perpage=20$level=1'
        self.regions_request_url = 'http://htmlweb.ru/geo/api.php?country=ru&json&api_key={api_key}&perpage=20$level=1'

        self.cities_source = 'sources/cities_list.txt'
        self.regions_source = 'sources/regions_list.txt'

        self.cities_results = 'results/cities_list.txt'
        self.regions_results = 'results/regions_list.txt'

        self.format = format
        self.balance = balance

    def writer(self, path: str, data):
        """
        Метод записывает информацию. path - путь для записи (см. конструктор), data - информация для записи.
        """
        with open(
                path, 'w', encoding='utf-8'
        ) as file:
            file.write(str(data))

    def reader(self, path: str) -> dict:
        """
        Метод читает информацию и переводит её в выражения python (Например, из <str> в <dict>). path - путь для чтения.
        """
        with open(
                path, 'r', encoding='utf-8'
        ) as file:
            return ast.literal_eval(file.read())

    def format_regions_dict(self, regions_dict: dict) -> list:
        """
        Метод форматирует исходный словарь регионов и возвращает отформатированный словарь.
        По умолчанию, формат [{'region_name': 'region_iso'},]
        """
        final_list = []

        for count, values_list in regions_dict.items():
            global region_iso, region_name
            region_name = None
            region_iso = None

            region_dict = {}

            if type(values_list) is not int:
                for key_name, value in values_list.items():
                    if key_name == 'name':
                        region_name = values_list[key_name]

                    elif key_name == 'iso':
                        region_iso = values_list[key_name]

                region_dict[region_name] = region_iso
                final_list.append(region_dict)

        return final_list

    def write_all_regions_sources(self):
        """
        Метод делает запрос к api и записывает результат в источник регионов (см. путь в конструкторе)
        """
        response = requests.get(
            self.regions_request_url.format(
                api_key=self.api_key
            )
        )

        response_dict = response.json()

        with open(
                self.regions_source, 'w', encoding='utf-8'
        ) as file:
            file.write(str(response_dict))

        return response_dict

    def write_all_regions(self):
        """
        Метод последовательно выпоняет след. методы:
        1) write_all_regions_sources
        2) reader
        3) format_regions_dict
        4) writer
        """
        if self.balance >= 5:
            self.write_all_regions_sources()
            source_dict = self.reader(
                self.regions_source
            )
            formated_dict = self.format_regions_dict(
                source_dict
            )
            self.writer(
                self.regions_results, formated_dict
            )

            self.balance -= 5
            print('Список успешно создан')

        else:
            print('Не достаточно запросов на балансе')

    def get_region_id_by_short_name(self, region_iso_code: str) -> int:
        """
        Метод получает id региона из его краткого названия.
        """
        dict = self.reader(self.regions_source)

        global searched_region_id
        searched_region_id = ''

        for count, region_dict in dict.items():
            if type(region_dict) != int:
                for key, value in region_dict.items():
                    if key == 'id':
                        searched_region_id = value

                    elif key == 'iso':
                        if value == region_iso_code:
                            return searched_region_id

    def get_region_full_name_by_id(self, region_id: int) -> str:
        """
        Метод получает полное имя региона из его id.
        """
        dict = self.reader(self.regions_source)

        global search_status
        search_status = ''

        for count, region_dict in dict.items():
            if type(region_dict) != int:
                for key, value in region_dict.items():
                    if search_status == 'name':
                        return value

                    if key == 'id':
                        if value == region_id:
                            search_status = 'name'

    def write_cities_sources(self, region_id: int):
        """
        Метод делает запрос http api к городам региона, записывает результат в cities_source
        """
        response = requests.get(
            self.cities_request_url.format(
                api_key=self.api_key,
                region_num=region_id
            )
        ).json()

        self.writer(
            self.cities_source, response
        )
        print(type(response))
        return response

    def format_cities_dict(self, data: dict, region_id: int) -> dict:
        """
        Метод форматирует словарь с городами в формат [{'region_full_name': ['city_name',]},]
        """
        final_dict = {}
        cities_list = []
        region_full_name = self.get_region_full_name_by_id(region_id)

        global city_name
        city_name = None

        for count, city_dict in data.items():
            try:
                int(count)
                for key, value in city_dict.items():
                    if key == 'name':
                        city_name = value

                    elif key == 'area':
                        if region_id != value:
                            city_name = None
                        else:
                            cities_list.append(city_name)

            except:
                pass

        cities_list = sorted(list(set(cities_list)))

        final_dict[region_full_name] = cities_list
        return final_dict

    def append_cities_results_list(self, path: str, data):
        """
        Метод дополняет словарь результатов городов
        """
        cities_list = []

        try:
            cities_list = self.reader(path)

        except:
            self.writer(self.cities_results, [])
            cities_list = []

        finally:
            cities_list.append(data)
            self.writer(path, cities_list)
