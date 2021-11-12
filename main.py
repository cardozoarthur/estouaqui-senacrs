import time
from modules.getTodayCalendar import todayCalendar
from modules.loginBlackboard import meetBlackBoard
from selenium.webdriver.common.action_chains import ActionChains
from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager as Chrome
from selenium.webdriver.chrome.options import Options

from dotenv import dotenv_values

env = dotenv_values(".env")

# Opções do driver
driver_opts = Options()
driver_opts.add_argument("--disable-infobars")
driver_opts.add_argument("--disable-extensions")
driver_opts.add_experimental_option("prefs", { \
    "profile.default_content_setting_values.media_stream_mic": 1, 
    "profile.default_content_setting_values.media_stream_camera": 1,
    "profile.default_content_setting_values.geolocation": 1, 
    "profile.default_content_setting_values.notifications": 1 
})


class main:
    def __init__(self, person_name, driver=webdriver.Chrome(Chrome().install(), options=driver_opts)):
        self.driver = driver
        print(f"Hello {person_name}!")
        self.calendar = todayCalendar(env["PORTAL_LOGIN"], env["PORTAL_SENHA"], env["COD_ALUNO"], self.driver)
        disciplina = self.calendar.get_today_calendar()[0]["descDisciplina"]

        self.blackboard = meetBlackBoard(env["BB_LOGIN"], env["BB_SENHA"], self.driver)

        self.blackboard.entry_meet(disciplina)

        time.sleep(5)
        self.blackboard.send_msg("Desculpa o atraso")
        time.sleep(1)
        self.blackboard.send_msg("Meu audio")
        self.blackboard.send_msg("está com problema")
        self.blackboard.send_msg("vou reiniciar aqui")

        time.sleep(0.5)
        self.driver.quit()

        
main("Arthur")