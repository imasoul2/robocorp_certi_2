from robocorp.tasks import task
from robocorp import browser

from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive

@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    browser.configure(
        slowmo=1000,
    )
    open_robot_order_website()
    orders = get_orders()
    fill_the_form(orders)
    archive_receipts()



def open_robot_order_website():
    """Open the intranet website"""

    browser.goto("https://robotsparebinindustries.com/")
    page = browser.page()
    page.click("text=Order your robot!")
    

def fill_the_form(sales_rep):
    """Fills in the sales data and click the 'Submit' button"""
    page = browser.page()

    for row in sales_rep:
        close_annoying_modal()
        page.select_option("#head", str(row["Head"]))
        page.check(f"#id-body-{str(row['Body'])}")
        page.fill("#address", row['Address'])
        page.fill("//label[contains(.,'3. Legs:')]/../input", row["Legs"])
        page.click("text=Preview")
        page.click("#order")
        # Keep trying until order button disappears
        while page.is_visible("#order"):
            page.click("#order")

        pdf_path = store_receipt_as_pdf(row["Order number"])
        png_path = screenshot_robot(row["Order number"])
        embed_screenshot_to_receipt(png_path, pdf_path)
        page.click("#order-another")



def get_orders():
    """Downloads file from the given URL and return the data in the file"""
    http = HTTP()
    http.download(url="https://robotsparebinindustries.com/orders.csv", overwrite=True)
    library = Tables()
    orders = library.read_table_from_csv(
        "orders.csv", columns=["Order number", "Head", "Body","Legs","Address"]
    )

    return orders

def close_annoying_modal():
    """Closes the annoying modal dialog"""
    page = browser.page()
    page.click("text=OK")

def log_out():
    """Presses the 'Log out' button"""
    page = browser.page()  
    page.click("text=Log out")


def collect_results():
    """Take a screenshot of the page"""
    page = browser.page()
    page.screenshot(path="output/sales_summary.png")


def store_receipt_as_pdf(order_number):
    """Export the data to a pdf file"""
    page = browser.page()
    sales_results_html = page.locator("#receipt").inner_html()
    path = f"output/{order_number}.pdf"
    pdf = PDF()
    pdf.html_to_pdf(sales_results_html, path)
    return path

def screenshot_robot(order_number):
    """Take a screenshot of the robot"""
    page = browser.page()
    path = f"output/{order_number}.png"
    page.screenshot(path=f"output/{order_number}.png")
    return path

def embed_screenshot_to_receipt(screenshot, pdf_file):
    """Embed the screenshot to the pdf file"""
    pdf = PDF()
    list_of_files = [
        pdf_file,
        screenshot
    ]
    pdf.add_files_to_pdf(
        files=list_of_files,
        target_document=pdf_file
    )

def archive_receipts():
    """Create a ZIP archive of the receipts and the images"""
    lib = Archive()
    lib.archive_folder_with_zip("output", "output/robot_orders.zip", include="*.pdf")
