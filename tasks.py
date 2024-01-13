from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.Tables import Tables
from robocorp.log import *
from RPA.PDF import PDF
from RPA.Archive import Archive

@task
def process_order_task():
    browser.configure(
        slowmo=100
    )

    open_robot_website()
    orders = get_orders()
    # loop_orders(orders)
    
    for order in orders:
        close_annoying_modal()
        receipt_number = fill_the_form(order)
        store_receipt_as_pdf(receipt_number)
        screenshot_robot(receipt_number)
        embed_screenshot_to_receipt(receipt_number)

        page = browser.page()
        page.click("css=#order-another")
        break
    
    archive_receipts()
    # screenshot()
    

def open_robot_website():
    browser.goto(url="https://robotsparebinindustries.com/#/robot-order")


def get_orders():
    http = HTTP()
    http.download("https://robotsparebinindustries.com/orders.csv", 'orders.csv', overwrite=True)

    table = Tables()
    data = table.read_table_from_csv('orders.csv')

    return data

def loop_orders(orders):
    for order in orders:
        info(f"Processing order: {order}")

def close_annoying_modal():
    page = browser.page()

    page.click("css=#root > div > div.modal > div > div > div > div > div > button.btn.btn-dark")

    info(page.content)

def fill_the_form(order):
    page = browser.page()

    page.select_option('#head', order['Head'])
    body_option = f"input[name='body'][value='{order['Body']}']"
    page.click(body_option)
    page.fill('xpath=/html/body/div[1]/div/div[1]/div/div[1]/form/div[3]/input', order['Legs'])
    page.fill('#address', order['Address'])
    page.click("css=#preview")

    page.screenshot(path=f"output/{order['Order number']}.png")

    return submit_order(page)

def submit_order(page, retries=3):
    receipt_number = None

    while True:
        page.click("css=#order")     
        
        if page.is_visible("css=#receipt"):
            receipt_number = page.inner_text("css=#receipt .badge")
            break
       
        page.wait_for_timeout(1000)
    
    return receipt_number



def store_receipt_as_pdf(order_number):
    pdf = PDF()
    
    pdf_filename = f"output/receipts/receipt_{order_number}.pdf"
    
    receipt_content = f""

    pdf.html_to_pdf(receipt_content, pdf_filename)
    
    return pdf_filename


def embed_screenshot_to_receipt(order_number):
    pdf = PDF()

    pdf.add_files_to_pdf(
        files=[f"output/screenshots/screenshot_{order_number}.png"], 
        target_document=f"output/receipts/receipt_{order_number}.pdf", 
        append=True
    )


def screenshot_robot(order_number):
    page = browser.page()
    screenshot_path = f"output/screenshots/screenshot_{order_number}.png"
    
    page.screenshot(path=screenshot_path)


def archive_receipts():
    lib = Archive()
    lib.archive_folder_with_zip('output/receipts', 'receipts.zip')