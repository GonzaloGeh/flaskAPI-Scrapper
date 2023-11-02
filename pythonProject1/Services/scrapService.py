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
from Schemas.SearchParametersModel import SearchParametersModel

TIME_TO_WAIT_IN_SECONDS = 2

def scrapSouthCarolina(searchParametersModel: SearchParametersModel):
    print(searchParametersModel)
    driver = None
    response_content = ""

    try:
        print("ok")
        driver = uc.Chrome() # Instance of a driver, called driver
        driver.get(searchParametersModel.baseUrl) # Getting the initial page
        print(f"Getting {searchParametersModel.baseUrl} site.")
        time.sleep(TIME_TO_WAIT_IN_SECONDS)
        wait = WebDriverWait(driver, 10)
        print("Clicking on Allendale County")
        link = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@id='rightsidebartext']//a[3]"))) # Clicking on Allendale County
        link.click()
        link = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@value='Accept']"))) # Clicking on accept
        link.click()
        input_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//input[@id='ContentPlaceHolder1_TextBoxlastName']")))
        print(f"Performing the search: {searchParametersModel.lastName}")
        input_element.send_keys(searchParametersModel.lastName) # Submitting the name.
        link = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@name='ctl00$ContentPlaceHolder1$ButtonSearch']")))
        link.click()
        time.sleep(TIME_TO_WAIT_IN_SECONDS)

        # Navegation done, from now on, we should get the list of offenders and click on those params, to get the offender page.
        searchResults = driver.page_source # Getting the page source
        response_content = f"""<div name='root'>
        <div name='searchResults>{searchResults}</div>"""
        # file = open(file_path, "w")
        # file.write("<div name='root'>")
        # file.write(f"<div name='searchResults>{searchResults}</div>")
        htmlPage = html.fromstring(searchResults) # Saving the htmlPage into a variable
        caseNumberList = htmlPage.xpath("//table[@class='searchResultsGrid']//a") # Getting the list
        time.sleep(TIME_TO_WAIT_IN_SECONDS)
        print(f"Found {len(caseNumberList)} results")
        # Getting 2 results, then we should get into each one of them.
        for index, memoryPosition in enumerate(caseNumberList):
            print(f"Looping through result number {index+1}.")
            xpath_expression = f"(//table[@class='searchResultsGrid']//a)[{index + 1}]"
            link = wait.until(EC.element_to_be_clickable((By.XPATH, xpath_expression))) 
            link.click()
            time.sleep(TIME_TO_WAIT_IN_SECONDS)
            casePartiesPage = driver.page_source
            html_page = html.fromstring(casePartiesPage)
            caseNumber = html_page.xpath("//td[@class='dataLabel'][contains(.,'Case Number')]/following-sibling::td[1]/text()")
            caseNumber = caseNumber[0]
            print("Saving case: " + caseNumber)
            link = wait.until(EC.element_to_be_clickable((By.XPATH, '//span[@id="__tab_ContentPlaceHolder1_TabContainerCaseDetails_TabPanel2"]'))) 
            link.click()
            time.sleep(TIME_TO_WAIT_IN_SECONDS)
            chargesPage = driver.page_source
            link = wait.until(EC.element_to_be_clickable((By.XPATH, '//span[@id="__tab_ContentPlaceHolder1_TabContainerCaseDetails_TabPanel5"]'))) 
            link.click()
            time.sleep(TIME_TO_WAIT_IN_SECONDS)
            actionsPage = driver.page_source
            link = wait.until(EC.element_to_be_clickable((By.XPATH, '//span[@id="__tab_ContentPlaceHolder1_TabContainerCaseDetails_TabPanel6"]'))) 
            link.click()
            time.sleep(TIME_TO_WAIT_IN_SECONDS)
            financialsPage = driver.page_source
            print("Saving the information on a txt.")
            
            response_content += f"""<div name='offender'>
            <div name='offenderInfo'>{caseNumber}</div>
            <div name='offenderCasePartiesPage'>{casePartiesPage}</div>
            <div name='offenderChargesPage'>{chargesPage}</div>
            <div name='offenderActionsPage'>{actionsPage}</div>
            <div name='offenderFinancialPage'>{financialsPage}</div>
            </div>"""
            # file.write("<div name='offender'>")
            # file.write(f"<div name='offenderInfo'>{caseNumber}</div>")
            # file.write(f"<div name='offenderCasePartiesPage'>{casePartiesPage}</div>")
            # file.write(f"<div name='offenderChargesPage'>{chargesPage}</div>")
            # file.write(f"<div name='offenderActionsPage'>{actionsPage}</div>")
            # file.write(f"<div name='offenderFinancialPage'>{financialsPage}</div>")
            # file.write("</div>")

            #print(f"HTML code for {caseNumber} saved to {file_path}")
            print("Pages visited. Going back to perform the search again.")
            driver.get(searchParametersModel.baseUrl) # Getting the initial page again, so we can perform the search.
            time.sleep(TIME_TO_WAIT_IN_SECONDS)
            wait = WebDriverWait(driver, 10)
            link = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@id='rightsidebartext']//a[3]"))) # Clicking on Allendale County
            link.click()
            link = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@value='Accept']"))) # Clicking on accept
            link.click()
            input_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//input[@id='ContentPlaceHolder1_TextBoxlastName']")))
            input_element.send_keys(searchParametersModel.lastName) # Submitting the name.
            link = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@name='ctl00$ContentPlaceHolder1$ButtonSearch']")))
            link.click()
            time.sleep(TIME_TO_WAIT_IN_SECONDS)
            response_content += "</div>"
        # file.write()
        # file.close()
        print("Python scraper finished execution. Connecting with the API so we can get the data from WH.")
        driver.close()
        print("end function")
    
    except WebDriverException as e:
        print(f"An error occurred: {e}")
        
    finally:
        driver.quit()

    return response_content