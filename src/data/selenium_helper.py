from selenium import webdriver 
from selenium.webdriver import Chrome 
from selenium.webdriver.common.by import By 
from selenium.common.exceptions import NoSuchElementException


def initiate_selenium():
    # Define the Chrome webdriver options
    options = webdriver.ChromeOptions() 
    options.add_argument("--headless") # Set the Chrome webdriver to run in headless mode for scalability
    options.add_argument("--use-fake-ui-for-media-stream")
    options.add_experimental_option('excludeSwitches', ['enable-logging'])

    # By default, Selenium waits for all resources to download before taking actions.
    # However, we don't need it as the page is populated with dynamically generated JavaScript code.
    options.page_load_strategy = "none"

    # Pass the defined options objects to initialize the web driver 
    driver = Chrome(options=options) 
    # Set an implicit wait of 5 seconds to allow time for elements to appear before throwing an exception
    driver.implicitly_wait(5)
    return driver


def find_element(selenium_item, selection_type, selector_name: str, friendly_name: str, type_cast: str=None, attribute: str=None, remove_strs: list=None, strip_char: str=None):
    try:
        found_object = selenium_item.find_element(selection_type, selector_name)
        found_object = found_object.text if attribute == 'text' else found_object.get_attribute(attribute)if attribute is not None else found_object
        if remove_strs is not None:
            for remove_str in remove_strs:
                if type(remove_str) is tuple:
                    found_object = found_object.replace(remove_str[0], remove_str[1])
                else:
                    found_object = found_object.replace(remove_str, "")
        found_object = found_object.strip()
        if strip_char is not None:
            found_object = found_object.strip(strip_char)
        if type_cast == 'int':
            found_object = int(found_object)
        elif type_cast == 'bool':
            found_object = True if found_object.lower() == 'yes' else False if found_object.lower() == 'no' else None
    except NoSuchElementException as nsex:
        print(f" - {friendly_name} not available")
        return None
    except Exception as ex:
        print(ex)
        raise ex
    return found_object