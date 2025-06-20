# llama_parser.py
import os
import time
import logging
import requests
from config import LLAMA_API_KEY

def check_job_status_and_get_results(job_id: str) -> str:
    """
    Checks the job status and retrieves results once the job is completed.
    Returns the structured Markdown output or an empty string if failed.
    """
    status_url = f"https://api.cloud.llamaindex.ai/api/parsing/job/{job_id}"
    headers = {"Authorization": f"Bearer {LLAMA_API_KEY}"}
    while True:
        try:
            response = requests.get(status_url, headers=headers)
            if response.status_code == 200:
                job_status = response.json().get("status")
                if job_status == "SUCCESS":
                    result_url = f"https://api.cloud.llamaindex.ai/api/parsing/job/{job_id}/result/markdown"
                    result_response = requests.get(result_url, headers=headers)
                    if result_response.status_code == 200:
                        return result_response.json().get("markdown", "")
                    else:
                        logging.error(f"Error fetching results: {result_response.status_code} - {result_response.text}")
                        return ""
                elif job_status == "FAILED":
                    logging.error("Job failed!")
                    return ""
                else:
                    logging.info(f"Job status: {job_status}. Waiting for completion...")
                    time.sleep(10)
            else:
                logging.error(f"Error checking job status: {response.status_code} - {response.text}")
                return ""
        except Exception as e:
            logging.error(f"Exception while checking job status: {e}")
            return ""

def process_pdf_with_llamaparser(pdf_path: str) -> str:
    """
    Sends the combined PDF to the LlamaParser API and saves the structured output as Markdown.
    Returns the path to the markdown file, or None if processing fails.
    """
    headers = {
        'Authorization': f'Bearer {LLAMA_API_KEY}',
        'accept': 'application/json',
        'premium_mode': 'true',
    }
    try:
        with open(pdf_path, 'rb') as pdf_file:
            files = {"file": ("file.pdf", pdf_file, "application/pdf")}
            response = requests.post(
                "https://api.cloud.llamaindex.ai/api/parsing/upload",
                headers=headers,
                files=files
            )
        if response.status_code == 200:
            job_id = response.json().get("id")
            if job_id:
                logging.info(f"Job ID: {job_id}")
                structured_data = check_job_status_and_get_results(job_id)
                if structured_data:
                    md_file = os.path.join(os.path.dirname(pdf_path), "structured_data.md")
                    with open(md_file, "w", encoding="utf-8") as f:
                        f.write(structured_data)
                    logging.info(f"Structured data saved to: {md_file}")
                    return md_file
                else:
                    logging.error("Failed to retrieve structured data from LlamaParser.")
                    return None
            else:
                logging.error("No job ID received from LlamaParser.")
                return None
        else:
            logging.error(f"Error from LlamaParser: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        logging.error(f"Exception while processing PDF with LlamaParser: {e}")
        return None
