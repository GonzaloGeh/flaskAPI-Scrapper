# Imports
import undetected_chromedriver as uc
from lxml import html
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import WebDriverException
from flask import Flask, send_file, request, render_template, jsonify
from Schemas.SearchParametersModel import SearchParametersModel
from Services import scrapService as ScrapService
from flask_pydantic import validate
import os

# Global Variables
BASE_URL = "http://www.sccourts.org/caseSearch/"
TIME_TO_WAIT_IN_SECONDS = 2
app = Flask(__name__)

@app.route('/')
def inicio():
    opciones_dropdown = ['Servidor Encendido', 'Servidor Apagado']
    return render_template('index.html', opciones=opciones_dropdown)

@app.route('/bypass/', methods=['POST'])
@validate()
def bypassSite(body: SearchParametersModel):
    response = ScrapService.scrapSouthCarolina(body)
    # txt = f'{result_file_name}'

    #     return 'txt cant be found', 404
    # response = send_file(txt, as_attachment=True)
    # os.remove(txt)

    return response
# def bypass():
#     try:
#         data = request.json
#         primer_nombre = data.get('primerNombre')
#         segundo_nombre = data.get('segundoNombre')
#         fecha = data.get('fecha')
#
#         print(primer_nombre)
#
#         # Use the JSON data as needed in your logic
#         respuesta = f"Descargando archivo para {primer_nombre} {segundo_nombre} en la fecha {fecha}"
#         return jsonify({'mensaje': respuesta})
#     except Exception as e:
#         return jsonify({'error': str(e)})


@app.route('/descargar_archivo_rapido/<string:lastName>', methods=['GET'])
def descargar_archivo_rapido(lastName):
    print(lastName)
    NAME_TO_SUBMIT = lastName

    try:
        driver = uc.Chrome()  # Instance of a driver, called driver
        driver.get(BASE_URL)  # Getting the initial page
        print(f"Getting {BASE_URL} site.")
        time.sleep(TIME_TO_WAIT_IN_SECONDS)
        wait = WebDriverWait(driver, 10)
        print("Clicking on Allendale County")
        link = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//div[@id='rightsidebartext']//a[3]")))  # Clicking on Allendale County
        link.click()
        link = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@value='Accept']")))  # Clicking on accept
        link.click()
        input_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@id='ContentPlaceHolder1_TextBoxlastName']")))
        print(f"Performing the search: {NAME_TO_SUBMIT}")
        input_element.send_keys(NAME_TO_SUBMIT)  # Submitting the name.
        link = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//input[@name='ctl00$ContentPlaceHolder1$ButtonSearch']")))
        link.click()
        time.sleep(TIME_TO_WAIT_IN_SECONDS)

        # Navegation done, from now on, we should get the list of offenders and click on those params, to get the offender page.
        searchResults = driver.page_source  # Getting the page source
        htmlPage = html.fromstring(searchResults)  # Saving the htmlPage into a variable
        caseNumberList = htmlPage.xpath("//table[@class='searchResultsGrid']//a")  # Getting the list
        time.sleep(TIME_TO_WAIT_IN_SECONDS)
        print(f"Found {len(caseNumberList)} results")
        # Getting 2 results, then we should get into each one of them.
        for index, memoryPosition in enumerate(caseNumberList):
            print(f"Looping through result number {index + 1}.")
            xpath_expression = f"(//table[@class='searchResultsGrid']//a)[{index + 1}]"
            link = wait.until(EC.element_to_be_clickable((By.XPATH, xpath_expression)))
            link.click()
            time.sleep(TIME_TO_WAIT_IN_SECONDS)
            casePartiesPage = driver.page_source
            html_page = html.fromstring(casePartiesPage)
            caseNumber = html_page.xpath(
                "//td[@class='dataLabel'][contains(.,'Case Number')]/following-sibling::td[1]/text()")
            caseNumber = caseNumber[0]
            print("Saving case: " + caseNumber)
            link = wait.until(EC.element_to_be_clickable(
                (By.XPATH, '//span[@id="__tab_ContentPlaceHolder1_TabContainerCaseDetails_TabPanel2"]')))
            link.click()
            time.sleep(TIME_TO_WAIT_IN_SECONDS)
            chargesPage = driver.page_source
            link = wait.until(EC.element_to_be_clickable(
                (By.XPATH, '//span[@id="__tab_ContentPlaceHolder1_TabContainerCaseDetails_TabPanel5"]')))
            link.click()
            time.sleep(TIME_TO_WAIT_IN_SECONDS)
            actionsPage = driver.page_source
            link = wait.until(EC.element_to_be_clickable(
                (By.XPATH, '//span[@id="__tab_ContentPlaceHolder1_TabContainerCaseDetails_TabPanel6"]')))
            link.click()
            time.sleep(TIME_TO_WAIT_IN_SECONDS)
            financialsPage = driver.page_source
            print("Saving the information on a txt.")
            file_path = f"{caseNumber}.txt"
            with open(file_path, 'w') as file:
                file.write("<div name='root'>")
                file.write(f"<div name='searchResults>{searchResults}</div>'")
                file.write(f"<div name='offenderInfo'>{caseNumber}</div>")
                file.write(f"<div name='offenderCasePartiesPage'>{casePartiesPage}</div>")
                file.write(f"<div name='offenderChargesPage'>{chargesPage}</div>")
                file.write(f"<div name='offenderActionsPage'>{actionsPage}</div>")
                file.write(f"<div name='offenderFinancialPage'>{financialsPage}</div>")
                file.write("</div>")
                print(f"HTML code for {caseNumber} saved to {file_path}")
            print("Pages visited. Going back to perform the search again.")
            driver.get(BASE_URL)  # Getting the initial page again, so we can perform the search.
            time.sleep(TIME_TO_WAIT_IN_SECONDS)
            wait = WebDriverWait(driver, 10)
            link = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//div[@id='rightsidebartext']//a[3]")))  # Clicking on Allendale County
            link.click()
            link = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@value='Accept']")))  # Clicking on accept
            link.click()
            input_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//input[@id='ContentPlaceHolder1_TextBoxlastName']")))
            input_element.send_keys(NAME_TO_SUBMIT)  # Submitting the name.
            link = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//input[@name='ctl00$ContentPlaceHolder1$ButtonSearch']")))
            link.click()
            time.sleep(TIME_TO_WAIT_IN_SECONDS)
        print("Python scraper finished its execution. Connecting with the API so we can get the data from WH.")
        driver.close()

    except WebDriverException as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()

    txt = '6102P0258360.txt'
    if not os.path.exists(txt):
        return "File doesn't exist", 404
    return send_file(txt, as_attachment=True)

@app.route('/descargar_archivo', methods=['POST'])
def descargar_archivo():
    opcion_seleccionada = request.form['opcion']
    # Aquí puedes realizar la acción deseada según la opción seleccionada
    # Por ejemplo, puedes descargar el archivo correspondiente a la opción.
    # Luego, puedes retornar una respuesta a la interfaz web.
    return f"Has seleccionado: {opcion_seleccionada}"
def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('No se puede finalizar la aplicación. '
                           'Es probable que no se esté ejecutando en el servidor Werkzeug.')
    func()

@app.route('/finalizar', methods=['GET'])
def finalizar_aplicacion():
    # Realiza cualquier limpieza o tareas necesarias antes de finalizar

    # Aquí estás finalizando la aplicación Flask
    shutdown_server()
    return 'Aplicación finalizada'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)