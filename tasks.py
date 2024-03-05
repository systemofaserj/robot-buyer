from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive



@task
def order_robots_from_rsb():
    """
    buy robots from RobotSpareBin
    saves the order info and a screenshot in a PDF file
    creates a ZIP archive with all data
    """
    browser.configure() #slowmo=100
    
    orders = get_orders()
    open_browser_and_page()
    for order in orders:
        close_modal()
        fill_data_form(order)
        order_robot()
        extract_order_data(order['Order number'])
        order_another_robot()
    archive_receipts()


def get_orders():
    get_orders_data_from_internet()
    data = get_data_from_file_as_table()
    return data


def get_orders_data_from_internet():
    http = HTTP()
    http.download('https://robotsparebinindustries.com/orders.csv', overwrite=True)
    
def get_data_from_file_as_table():
    file_reader = Tables()
    csv_file = file_reader.read_table_from_csv('orders.csv', columns=["Order number","Head","Body","Legs","Address"])
    return csv_file

def open_browser_and_page():
    page = browser.goto('https://robotsparebinindustries.com/#/robot-order')
    
def close_modal():
    is_still_visible = True
    page = browser.page()

    while is_still_visible:
        page.click("button:text('Yep')")
        is_still_visible = page.is_visible('#root > div > div.modal > div > div > div')
    
def fill_data_form(order):
    page = browser.page()
    page.select_option("#head", order['Head'])
    page.click("#id-body-"+str(order['Body']))
    page.fill('//*[@placeholder="Enter the part number for the legs"]', order['Legs'])
    page.fill('#address', order['Address'])

def get_preview_robot():
    page = browser.page()
    page.click('text=Preview')
    # TODO: screenshot
    
def order_robot():
    is_order_ok = False
    page = browser.page()
    while not is_order_ok:
        page.click("button:text('Order')")
        is_order_ok = check_order_succesfuly()
    
    
    
def check_order_succesfuly():
    page = browser.page()
    return page.is_visible('#order-another')

def take_screenshot(robbot_number):
    path = 'output/screenshots/robbot_{}.png'.format(robbot_number)
    page = browser.page()
    page = page.screenshot(path=path)
    return path

def store_receipt_pdf(order_n):
    page = browser.page()
    receipt_html = page.locator("#receipt").inner_html()
    pdf_path = "output/receipts/receipt_{}.pdf".format(order_n)
    pdf = PDF()
    pdf = pdf.html_to_pdf(receipt_html, pdf_path)
    return pdf_path

def order_another_robot():
    page = browser.page()
    page.click("button:text('Order another robot')")
    
def extract_order_data(order_n):
    screenshot = take_screenshot(order_n)
    pdf_file = store_receipt_pdf(order_n)
    embed_screenshot_to_receipt(pdf_file, screenshot)
    
def embed_screenshot_to_receipt(pdf_name, screenshot):
    pdf = PDF()
    pdf.add_files_to_pdf(files=[pdf_name,screenshot], target_document=pdf_name)
    
def archive_receipts():
    lib = Archive()
    lib.archive_folder_with_zip('output/receipts', 'output/receipts.zip')