import time
import random
import json
import pyautogui
from pyautogui import click, moveTo, typewrite
from datetime import datetime
from selenium.webdriver.common.action_chains import ActionChains
from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from seleniumwire.utils import decode
from webdriver_manager.chrome import ChromeDriverManager as Chrome

class meetBlackBoard:
    def __init__(self, login, password, driver):
        self.driver = driver
        self.login = login
        self.password = password
    
    def write_input(self, element, text):
        for character in text:
            actions = ActionChains(self.driver)
            actions.move_to_element(element)
            actions.click()
            actions.send_keys(character)
            actions.perform()
            time.sleep(random.uniform(0.01,0.02))

    def map_meet(self, element):
        text = str(element.get_attribute('innerText')).lower()
        return {"text": text, "element": element}

    def filter_meet(self, meet):
        if meet["text"] and "rs-" in meet["text"]:
            return True
        return False
    
    def filter_channel_buttons(self, button):
        if "channel-item" in button.get_attribute("id"):
            return True
        return False

    def filter_button(self, button):
            return bool("session" in button.get_attribute("id"))

    def toggle_menu(self):
        toggle_button = WebDriverWait(self.driver, 30).until(EC.presence_of_element_located(( By.CSS_SELECTOR, '.panel-open-control button:not(.ng-hide)' )))
        return toggle_button.click()

    def run_login(self):
        # Vá até a página do blackboard
        self.driver.get("https://senac.blackboard.com/")
        # Faça login na página do portal do aluno

        ## Pegue o input de login
        input_login = WebDriverWait(self.driver, 30).until(EC.presence_of_element_located(( By.ID, "user_tmp" )))

        ## Pegue o input de senha
        input_password = WebDriverWait(self.driver, 30).until(EC.presence_of_element_located(( By.ID, "password" )))

        ## Pegue o botão
        btn_login = WebDriverWait(self.driver, 30).until(EC.presence_of_element_located(( By.ID, "entry-login" )))
        time.sleep(0.2)
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(0.3)
        ## Escreva os dados
        self.write_input(input_login, self.login)
        self.write_input(input_password, self.password)

        ## Efetuar o clique no botâo de entrar
        btn_login.click()

    def get_classes(self):
        # Login
        self.run_login()

        classes = WebDriverWait(self.driver, 30).until(EC.presence_of_all_elements_located(( By.CSS_SELECTOR, ".courseListing li" )))
        classes_mapped = map(self.map_meet, classes)
        classes_filtered = filter(self.filter_meet, list(classes_mapped))

        return classes_filtered
    
    def select_meet(self, meet_name):
        meet_name = str(meet_name).lower()
        classes = self.get_classes()
        for meet_class in classes:
            if meet_name in meet_class["text"]:
                link = meet_class["element"].find_element(By.CSS_SELECTOR, 'a')
                time.sleep(0.5)
                link.click()
    
    def get_page_token(self):
        url = self.driver.current_url
        l = str(url).split('/')
        l.reverse()
        return l[0]

    def get_secure_link(self):
        page_token = self.get_page_token()
        secure_link_uri = f'/collab/api/csa/sessions/{page_token}/url'
        self.driver.wait_for_request(secure_link_uri, 10)
        requests = self.driver.requests
        for request in requests:
            if request.response:
                response = request.response
                if request.url == "https://ca-lti.bbcollab.com"+secure_link_uri:
                    body = decode(response.body, response.headers.get('Content-Encoding', 'identity'))
                    return body

    def accept_infos(self):
        # .button.confirm + .button.confirm + .start-tutorial-button
        btn_to_click = WebDriverWait(self.driver, 30).until(EC.presence_of_element_located(( By.CSS_SELECTOR, '.button.confirm' )))
        btn_to_click.click()
        time.sleep(0.3)
        btn_to_click = WebDriverWait(self.driver, 30).until(EC.presence_of_element_located(( By.CSS_SELECTOR, '.button.confirm' )))
        btn_to_click.click()
        time.sleep(0.3)
        btn_to_click = WebDriverWait(self.driver, 30).until(EC.presence_of_element_located(( By.CSS_SELECTOR, '.later-tutorial-button' )))
        btn_to_click.click()
        time.sleep(0.3)
        btn_to_click = WebDriverWait(self.driver, 30).until(EC.presence_of_element_located(( By.CSS_SELECTOR, '#tutorial-dialog-tutorials-menu-learn-about-tutorials-menu-close' )))
        btn_to_click.click()

    def entry_meet(self, meet_name):
        self.select_meet(meet_name)
        span = WebDriverWait(self.driver, 30).until(EC.presence_of_element_located(( By.CSS_SELECTOR, 'span[title="Webconferência"]' )))
        a = span.find_element(By.XPATH, '..')
        a.click()
        time.sleep(0.5)
        iframe = WebDriverWait(self.driver, 30).until(EC.presence_of_element_located(( By.CSS_SELECTOR, 'iframe' )))
        iframe_src = iframe.get_attribute('src')
        time.sleep(0.5)
        self.driver.get(iframe_src)
        time.sleep(1)
        buttons = WebDriverWait(self.driver, 30).until(EC.presence_of_all_elements_located(( By.CSS_SELECTOR, "button[id]" )))
        time.sleep(1)
        button = list(filter(self.filter_button, buttons))
        time.sleep(1)
        button[0].click()
        time.sleep(2)
        secure_link_data = self.get_secure_link()
        secure_link_json = json.loads(secure_link_data)
        self.driver.get(secure_link_json["url"])
        time.sleep(10)
        self.accept_infos()
        time.sleep(10)
        self.reply_call()

    def select_all_channel(self):
        # chat-channels__list menu-list ng-isolate-scope
        buttons = WebDriverWait(self.driver, 30).until(EC.presence_of_all_elements_located(( By.CSS_SELECTOR, 'button' )))
        channel_buttons = filter(self.filter_channel_buttons, buttons)
        channel_buttons_list = list(channel_buttons)
        channel_buttons_list[0].click()

        return

    def reply_call(self):
        time.sleep(1)
        self.toggle_menu()
        time.sleep(1)
        self.select_all_channel()
        time.sleep(3)
        input_text = WebDriverWait(self.driver, 30).until(EC.presence_of_element_located(( By.CSS_SELECTOR, '.ql-editor' )))
        self.write_input(input_text, 'Boa noite')
        time.sleep(1)
        send_btn = WebDriverWait(self.driver, 30).until(EC.presence_of_element_located(( By.CSS_SELECTOR, 'button[data-testid=text-editor-send-message]' )))
        time.sleep(0.1)
        send_btn.click()
    
    def send_msg(self, message):
        input_text = WebDriverWait(self.driver, 30).until(EC.presence_of_element_located(( By.CSS_SELECTOR, '.ql-editor' )))
        self.write_input(input_text, str(message))
        time.sleep(1)
        send_btn = WebDriverWait(self.driver, 30).until(EC.presence_of_element_located(( By.CSS_SELECTOR, 'button[data-testid=text-editor-send-message]' )))
        time.sleep(0.1)
        send_btn.click()
        

# meetBlackBoard(login, senha).entry_meet("Qualidade de Software")
# time.sleep(60*60*12)