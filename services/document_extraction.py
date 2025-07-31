import cv2
import pytesseract
import easyocr
from pdf2image import convert_from_path
from openai import OpenAI
from queries.document_extration_query import document_extraction_query
from config import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)

class DocumentExtractor:

    def __init__(self):
        pass

    def extract_text_from_image(self, image_path: str, use_easyocr=False):
        """Extracts text from an image using Tesseract OCR or EasyOCR."""
        if use_easyocr:
            reader = easyocr.Reader(['en'])
            text = reader.readtext(image_path, detail=0)
            return " ".join(text)
        else:
            image = cv2.imread(image_path)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            return pytesseract.image_to_string(gray)

    def extract_text_from_pdf(self, pdf_path: str):
        """Extracts text from a PDF by converting pages to images and applying OCR."""
        images = convert_from_path(pdf_path)
        full_text = ""
        for image in images:
            text = pytesseract.image_to_string(image)
            full_text += text + "\n"
        return full_text

    async def extract_data_from_llm(self, text: str, system_prompt):
        required_system_prompt = "Summarize the following text."
        if system_prompt:
            required_system_prompt = system_prompt
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": required_system_prompt},
                {"role": "user", "content": text}
            ]
        )
        return response.choices[0].message.content

    async def summarize(self, file_path: str):
        """Determines file type and extracts text accordingly, then summarizes it."""
        if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):
            extracted_text = self.extract_text_from_image(file_path)
        elif file_path.lower().endswith('.pdf'):
            extracted_text = self.extract_text_from_pdf(file_path)
        else:
            print("Unsupported file format.")
            return

        print("Extracted Text:\n", extracted_text)

        extraction_result = await self.extract_data_from_llm(extracted_text)
        return extraction_result
    
    async def extract(self, file_path:str):
        if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):
            extracted_text = self.extract_text_from_image(file_path)
        elif file_path.lower().endswith('.pdf'):
            extracted_text = self.extract_text_from_pdf(file_path)
        else:
            print("Unsupported file format.")
            return
        
        extraction_result_text = await self.extract_data_from_llm(extracted_text, document_extraction_query())
        return extraction_result_text