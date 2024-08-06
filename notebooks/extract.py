import json
import re
import uuid
import numpy as np
from layoutparser.models.detectron2 import Detectron2LayoutModel

import pdfplumber

from tqdm import tqdm
from PIL import Image
from io import BytesIO
from pathlib import Path
from pdfplumber.page import CroppedPage, Page

def clean_text(s: str) -> str:
    # remove un used strings like 
    s = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\xff]', ' ', s)
    # if three spaces or more, replace with empty string
    s = re.sub(r' {3,}', '', s)
    return s

def inference_page(p: Page | CroppedPage, model: Detectron2LayoutModel) -> tuple:
    img = p.to_image()
    imgfile = BytesIO()
    img.save(imgfile, format='png', quantize=False)
    img = np.array(Image.open(imgfile).convert('RGB'))
    blocks = model.detect(img)
    return blocks, img

def extract_text_from_block(
        p: Page|CroppedPage, 
        page_num: int, 
        model: Detectron2LayoutModel, 
        multimodal_dir: Path) -> str:
    blocks, img = inference_page(p, model)
    texts = []
    multimodals = []
    y_coords = [0.0]
    for block in blocks:
        if block.type in ('Figure', 'Table'):
            file_name = f'p{page_num}_{block.type}{len(multimodals)}'
            uid = uuid.uuid3(namespace=uuid.NAMESPACE_DNS, name=file_name)
            file_path = multimodal_dir / f'{file_name}_{uid}.png'
            im = p.crop(block.coordinates, relative=True, strict=False).to_image()
            im.save(file_path)
            multimodals.append(file_path.name)
            y_coords.extend([block.block.y_1, block.block.y_2])  # y_1, y_2
    y_coords.append(p.height)
    y_coords = sorted(y_coords)

    if len(y_coords) == 2:  # no multimodal
        processed_text = clean_text(p.extract_text())
    else:
        for i in range(0, len(y_coords)-1, 2):
            y1, y2 = y_coords[i], y_coords[i+1]
            cropped_page = p.crop((0.0, y1, p.width, y2), relative=True, strict=False)
            texts.append(clean_text(cropped_page.extract_text()))

        processed_text = '\n\n'.join(texts)
    
    return processed_text, multimodals

def main(pages):
    # lp://PubLayNet/faster_rcnn_R_50_FPN_3x/config
    # lp://PubLayNet/mask_rcnn_X_101_32x8d_FPN_3x/config
    model = Detectron2LayoutModel(
        'lp://PubLayNet/mask_rcnn_X_101_32x8d_FPN_3x/config', 
        extra_config=["MODEL.ROI_HEADS.SCORE_THRESH_TEST", 0.8],
        label_map={0: "Text", 1: "Title", 2: "List", 3: "Table", 4: "Figure"}
    )
    # process first page
    multimodal_dir = Path('./fis_issue22_3_multimodal')
    if not multimodal_dir.exists():
        multimodal_dir.mkdir()

    page_num = 0
    first_page = pages[page_num]
    data = [dict(page_content=first_page.extract_text(), metadata={'page': page_num, 'multimodals': []})]
    page_num += 1
    # process the rest of the pages
    for page in tqdm(pages[1:], desc='Processing pages', total=len(pages)-1):
        if page.height > page.width:
            # vertical page
            processed_text, multimodals = extract_text_from_block(
                page, page_num, model, multimodal_dir)
            data.append(
                dict(
                    page_content=processed_text,
                    metadata={'page': page_num, 'multimodals': multimodals}
                )
            )
            page_num += 1
        else:
            left = page.crop((0.0, 0.0, 0.5*page.width, page.height), relative=True)
            right = page.crop((0.5*page.width, 0.0, page.width, page.height), relative=True)
            for sub_page in [left, right]:
                processed_text, multimodals = extract_text_from_block(
                    sub_page, page_num, model, multimodal_dir)
                data.append(
                    dict(
                        page_content=processed_text,
                        metadata={'page': page_num, 'multimodals': multimodals}
                    )
                )
                page_num += 1

    with open('fis_issue22_3.json', 'w') as f:
        json.dump(data, f, indent=2)

if __name__ == '__main__':
    file_path = Path("fis_issue22-3.pdf").resolve()
    pdf = pdfplumber.open(file_path)
    pages = pdf.pages
    main(pages)