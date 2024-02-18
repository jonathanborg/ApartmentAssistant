import re
import time
import requests
from bs4 import BeautifulSoup


def initiate_request(url: str=None):
    session = requests.Session()
    time.sleep(1)
    response = session.get(url, headers={"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36"})
    time.sleep(1)
    page = BeautifulSoup(response.text, 'html.parser')
    return page


def find_element(content, html_tag: str, class_name: str, friendly_name: str, custom_name: dict=None, type_cast: str=None, attribute: str=None, remove_strs: list=None, strip_char: str=None):
    try:
        if class_name is None:
            found_object = content.find(html_tag).get(custom_name)
        else:
            found_object = content.find(html_tag, {'class': class_name})
            found_object = found_object.text if attribute == 'text' else found_object.get(attribute) if attribute is not None else found_object

        if remove_strs is not None:
            for remove_str in remove_strs:
                if type(remove_str) is tuple:
                    found_object = found_object.replace(remove_str[0], remove_str[1])
                else:
                    found_object = found_object.replace(remove_str, "")
        if type_cast is not None:
            found_object = re.sub("\s\s+" , " ", found_object)
            found_object = found_object.strip()
        if strip_char is not None:
            found_object = found_object.strip(strip_char)
        if type_cast == 'int':
            found_object = int(found_object)
        elif type_cast == 'bool':
            found_object = 'No' if found_object.lower() == 'no' or 'not present' in found_object.lower() else 'Yes' if found_object.lower() == 'yes' or 'present' in found_object.lower() else 'Unknown'
    except AttributeError as aex:
        print(f" - {friendly_name} not found")
        return ''
    except Exception as ex:
        print(ex)
        raise ex
    return found_object