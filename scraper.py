# scraper.py
import os
import time
import logging
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from PyPDF2 import PdfMerger
from PIL import Image
from reportlab.pdfgen import canvas

def navigate_to_url(url: str) -> tuple[str, str]:
    """
    Uses Selenium in headless mode to obtain the page source and final URL.
    Returns (page_source, final_url) or (None, None) on failure.
    """
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    driver = None
    try:
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
        driver.get(url)
        time.sleep(3)  # Allow time for the page to load
        page_source = driver.page_source
        final_url = driver.current_url
        return page_source, final_url
    except Exception as e:
        logging.error(f"Error navigating to {url}: {e}")
        return None, None
    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass

def download_file(url: str, save_path: str) -> bool:
    """
    Downloads a file from a URL to the specified path.
    Returns True if successful, otherwise False.
    """
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, stream=True, headers=headers, timeout=30)
        response.raise_for_status()
        with open(save_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    file.write(chunk)
        logging.info(f"Downloaded: {save_path}")
        return True
    except requests.RequestException as e:
        logging.error(f"Failed to download {url}: {e}")
        return False

def scrape_page(url: str, scrape_images: bool = True, scrape_pdfs: bool = True) -> str:
    """
    Scrapes a webpage, saving text, and conditionally images and PDFs.
    Returns the directory name where the content is saved or None if failed.
    """
    html_content, final_url = navigate_to_url(url)
    if not html_content or not final_url:
        logging.error(f"Failed to retrieve content from {url}")
        return None
    soup = BeautifulSoup(html_content, "html.parser")
    text_content = soup.get_text(separator='\n', strip=True)
    
    # Create a directory based on the domain
    domain = urlparse(final_url).netloc.replace('.', '_')
    os.makedirs(domain, exist_ok=True)
    
    # Save text content
    text_file = os.path.join(domain, "page_content.txt")
    try:
        with open(text_file, 'w', encoding='utf-8') as file:
            file.write(text_content)
    except Exception as e:
        logging.error(f"Error saving text content to {text_file}: {e}")
    
    # Download images if enabled
    if scrape_images:
        for img_tag in soup.find_all('img'):
            src = img_tag.get('src')
            if src:
                img_url = urljoin(final_url, src)
                if img_url.lower().endswith(('.jpg', '.jpeg', '.png')):
                    img_name = os.path.basename(urlparse(img_url).path) or f"image_{os.urandom(4).hex()}.jpg"
                    img_save_path = os.path.join(domain, img_name)
                    download_file(img_url, img_save_path)
    
    # Download PDFs if enabled
    if scrape_pdfs:
        for link in soup.find_all('a', href=True):
            file_url = urljoin(final_url, link['href'])
            if file_url.lower().endswith('.pdf'):
                pdf_name = os.path.basename(urlparse(file_url).path) or f"file_{os.urandom(4).hex()}.pdf"
                pdf_save_path = os.path.join(domain, pdf_name)
                download_file(pdf_url := file_url, pdf_save_path)
    
    return domain

def combine_text_images_pdfs(dir_name: str, output_pdf_path: str) -> str:
    """
    Combines text (converted to PDF), images (converted to PDF), and existing PDFs into one PDF.
    Returns the path to the combined PDF.
    """
    merger = PdfMerger()
    temp_pdfs = []
    
    # Convert text to PDF
    text_file = os.path.join(dir_name, "page_content.txt")
    if os.path.exists(text_file):
        temp_text_pdf = os.path.join(dir_name, "text_content.pdf")
        try:
            c = canvas.Canvas(temp_text_pdf)
            with open(text_file, 'r', encoding='utf-8') as tf:
                lines = tf.readlines()
                y = 800
                for line in lines:
                    if y < 50:
                        c.showPage()
                        y = 800
                    c.drawString(50, y, line.strip())
                    y -= 15
            c.save()
            merger.append(temp_text_pdf)
            temp_pdfs.append(temp_text_pdf)
        except Exception as e:
            logging.error(f"Error converting text to PDF for {text_file}: {e}")
    
    # Convert images to PDFs
    for file in os.listdir(dir_name):
        if file.lower().endswith(('.jpg', '.jpeg', '.png')):
            image_path = os.path.join(dir_name, file)
            image_pdf = os.path.join(dir_name, f"{os.path.splitext(file)[0]}.pdf")
            try:
                Image.open(image_path).convert("RGB").save(image_pdf)
                merger.append(image_pdf)
                temp_pdfs.append(image_pdf)
            except Exception as e:
                logging.error(f"Error processing image {image_path}: {e}")
    
    # Append existing PDFs (skip temporary ones and the output file)
    for file in os.listdir(dir_name):
        if file.lower().endswith('.pdf'):
            pdf_path = os.path.join(dir_name, file)
            if pdf_path not in temp_pdfs and os.path.basename(pdf_path) != os.path.basename(output_pdf_path):
                try:
                    merger.append(pdf_path)
                except Exception as e:
                    logging.error(f"Error appending PDF {pdf_path}: {e}")
    
    try:
        merger.write(output_pdf_path)
        merger.close()
    except Exception as e:
        logging.error(f"Error writing combined PDF to {output_pdf_path}: {e}")
    
    # Clean up temporary PDF files
    for temp_pdf in temp_pdfs:
        try:
            if os.path.exists(temp_pdf):
                os.remove(temp_pdf)
        except Exception as e:
            logging.warning(f"Failed to remove temporary file {temp_pdf}: {e}")
    
    return output_pdf_path
