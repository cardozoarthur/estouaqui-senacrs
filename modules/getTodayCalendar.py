import time
import random
import json
from datetime import datetime
from selenium.webdriver.common.action_chains import ActionChains
from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from seleniumwire.utils import decode
from webdriver_manager.chrome import ChromeDriverManager as Chrome


class todayCalendar:
    def __init__(self, login, password, code, driver):
        self.driver = driver
        self.login = login
        self.password = password
        self.code = code
    
    def write_input(self, element, text):
        for character in text:
            actions = ActionChains(self.driver)
            actions.move_to_element(element)
            actions.click()
            actions.send_keys(character)
            actions.perform()
            time.sleep(random.uniform(0.01,0.08))

    def filter_today(self, obj):
        now = datetime.now()
        formattedDay = now.strftime("%Y-%m-%d")
        formattedHour = now.strftime("%H:%M:%S")
        if obj["data"] and obj["data"] == formattedDay and obj["horaInicio"] and obj["horaInicio"] >= formattedHour:
            return True
        return False
    
    def sort_hour(self, obj):
        return obj["horaInicio"]

    def run_login(self):
        # Vá até a página do portal do aluno
        self.driver.get("https://apsweb.senacrs.com.br/modulos/aluno/login.php5?")
        # Faça login na página do portal do aluno

        ## Pegue o input de login
        input_login = WebDriverWait(self.driver, 30).until(EC.presence_of_element_located(( By.ID, "usr-login" )))

        ## Pegue o input de senha
        input_password = WebDriverWait(self.driver, 30).until(EC.presence_of_element_located(( By.ID, "usr-password" )))

        ## Pegue o botão
        btn_login = WebDriverWait(self.driver, 30).until(EC.presence_of_element_located(( By.ID, "btnEntrar" )))

        ## Escreva os dados
        self.write_input(input_login, self.login)
        self.write_input(input_password, self.password)

        ## Efetuar o clique no botâo de entrar
        btn_login.click()

    def get_calendar(self):
        # Login
        self.run_login()

        # Se direcionar para a página do calendário
        self.driver.get("https://apsweb.senacrs.com.br/modulos/aluno/agendaAluno.php5?codigoAluno="+codigoAluno)

        ## Espere o calendario
        calendario = WebDriverWait(self.driver, 30).until(EC.presence_of_element_located(( By.ID, "calAluno" )))

        self.driver.wait_for_request('/modulos/aluno/agendaAluno.php5', 10)

        time.sleep(20)
        requests = self.driver.requests

        for request in requests:
            if request.response:
                response = request.response
                if request.url == "https://apsweb.senacrs.com.br/modulos/aluno/agendaAluno.php5?codigoAluno="+codigoAluno and request.method == "POST":
                    body = decode(response.body, response.headers.get('Content-Encoding', 'identity'))
                    return body
    
    def get_today_calendar(self):
        calendar = json.loads(self.get_calendar())
        # print(calendar["data"])
        data = calendar["data"]
        filtered = filter(self.filter_today, data)
        return list(filtered)

# print(todayCalendar(login, senha, codigoAluno).get_today_calendar()[0]["descDisciplina"])