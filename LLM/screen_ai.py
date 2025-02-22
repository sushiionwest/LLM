import os
import time
import requests
import json
from PIL import Image
import pytesseract
import subprocess
import datetime
import logging
import argparse

# LM Studio API URL updated to use your server
API_URL = "http://192.168.0.128:8080/v1/chat/completions"

# Default paths for screenshots and logs
DEFAULT_SCREENSHOT_PATH = "screenshot.png"
DEFAULT_LOG_FILE = "screen_ai_log.txt"

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Configure Tesseract OCR for better accuracy
pytesseract.pytesseract.tesseract_cmd = "/opt/homebrew/bin/tesseract"  # Ensure this path is correct
OCR_CONFIG = "--psm 4"  # Page Segmentation Mode: Assumes a block of text

def capture_screen(screenshot_path):
    try:
        # If you get "access denied", ensure your Terminal/IDE has Screen Recording permission in System Preferences:
        # System Preferences -> Security & Privacy -> Privacy -> Screen Recording.
        subprocess.run(["screencapture", "-x", screenshot_path], check=True)
        return screenshot_path
    except subprocess.CalledProcessError as e:
        logging.error(f"Screen capture failed: {str(e)}")
        return None

def extract_text(image_path):
    try:
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img, config=OCR_CONFIG).strip()
        return text if text else None  # Return None if text is empty
    except Exception as e:
        logging.error(f"OCR error: {str(e)}")
        return None

def query_ai(text):
    # Prepare payload without a fixed max_tokens parameter
    payload = {
        "model": "deepseek-r1-distill-qwen-7b:2",
        "messages": [{"role": "user", "content": f"Analyze this text: {text}"}],
        "temperature": 0.7
    }
    try:
        response = requests.post(API_URL, headers={"Content-Type": "application/json"}, json=payload)
        response.raise_for_status()  # Raise exception for HTTP errors
        data = response.json()
        choices = data.get("choices")
        if choices and len(choices) > 0:
            ai_response = choices[0].get("message", {}).get("content", "⚠️ No response received.")
            return ai_response
        else:
            logging.warning("API responded without valid choices.")
            return "⚠️ API responded without valid choices."
    except requests.exceptions.RequestException as e:
        logging.error(f"API request failed: {str(e)}")
        return f"⚠️ API Request Failed: {str(e)}"

def log_data(log_file, text, ai_response):
    try:
        with open(log_file, "a") as log:
            log.write(f"\n[{datetime.datetime.now()}]\nExtracted Text:\n{text}\nAI Response:\n{ai_response}\n{'='*50}\n")
    except Exception as e:
        logging.error(f"Failed to log data: {str(e)}")

def main(screenshot_path, log_file, delay):
    logging.info("Starting screen AI capture process ...")
    try:
        while True:
            logging.info("📸 Capturing screen...")
            screenshot = capture_screen(screenshot_path)
            if not screenshot:
                time.sleep(delay)
                continue

            logging.info("🔍 Extracting text from screenshot...")
            extracted_text = extract_text(screenshot)
            if extracted_text:
                logging.info(f"📝 Extracted Text:\n{extracted_text}")
                logging.info("🤖 Querying AI ...")
                ai_response = query_ai(extracted_text)
                logging.info(f"🎯 AI Response:\n{ai_response}")
                log_data(log_file, extracted_text, ai_response)
            else:
                logging.warning("⚠️ No text detected. Skipping AI query.")

            logging.info(f"⏳ Waiting {delay} seconds before next capture...\n")
            time.sleep(delay)
    except KeyboardInterrupt:
        logging.info("🛑 Program interrupted by user. Exiting...")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Screen AI Capture Script")
    parser.add_argument("--screenshot", type=str, default=DEFAULT_SCREENSHOT_PATH, help="Path to save the screenshot")
    parser.add_argument("--log", type=str, default=DEFAULT_LOG_FILE, help="Path to the log file")
    parser.add_argument("--delay", type=int, default=30, help="Delay between screen captures in seconds")
    args = parser.parse_args()
    main(args.screenshot, args.log, args.delay)
