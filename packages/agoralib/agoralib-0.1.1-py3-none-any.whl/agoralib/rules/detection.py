"""
@file detection.py
@brief Règle pour detecter des CC normalement jamais utilisée avec Arkindex (NOT CHECKED).
"""

from .base import BaseRule

import cv2
import numpy as np
import requests

class DetectionRule(BaseRule):
    """
    @class DetectionRule
    @brief Extract connected components from a IIIF image using binarisation.
           Requires one input bbox with a label and a IIIF URL.
    """

    def apply(self, bboxes, page_width, page_height):
    
        # check bboxes validity
        if not isinstance(bboxes, list) or len(bboxes) == 0:
            print("==> Error: 'bboxes' is empty or not a list.")
            return []

        box = bboxes[0]
        if not isinstance(box, dict):
            print("==> Error: First element in 'bboxes' is not a dictionary.")
            return []

        required_keys = ["label", "URL"]
        for key in required_keys:
            if key not in box:
                print(f"==> Error: Missing key '{key}' in the bounding box.")
                return []

        #check rule parameters
        page_label = self.params.get("label", None)
        new_label = self.params.get("new_label", None)
        threshold = int(self.params.get("threshold", None))
        areamin = float(self.params.get("areamin", None))
        
        if page_label is None or new_label is None or threshold is None or areamin is None:
            print("==> Error: somethings missing in rule parameters.")
            return []

        #check rule vs bboxes
        if box["label"] != page_label or not box["URL"]:
            print("==> Error: label or URL mismatch.")
            return []


        # Everythings ready for binarisation        
        img_url = box["URL"]
        print(f"==> Fetching IIIF image from {img_url}...")

        try:
            response = requests.get(img_url)
            response.raise_for_status()
            image_bytes = np.asarray(bytearray(response.content), dtype=np.uint8)
            img = cv2.imdecode(image_bytes, cv2.IMREAD_GRAYSCALE)  # chargement en niveau de gris
            if img is None:
                raise ValueError("OpenCV failed to decode image.")
        except Exception as e:
            print(f"==> Error: Unable to load image from URL: {e}")
            return []

        # Binarisation 
        if threshold == 0:
            print("==> threshold = 0 => otsu")
            _, binary = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        else:
            print("==> Binarisation => threshold = ",threshold)            
            _, binary = cv2.threshold(img, threshold, 255, cv2.THRESH_BINARY)            

        # Inversion (optionnel ? a verifier ?)
        binary = 255 - binary
        
        debug_path = "./log/img.png"
        cv2.imwrite(debug_path, img)
        debug_path = "./log/binarized.png"
        cv2.imwrite(debug_path, binary)
        print(f"==> Img/Binarized image saved to: {debug_path}")

        # Composantes connexes
        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(binary)

        components = []
        components.append(box) 
        print("==> Min ratio area to be added = ",areamin)   
        for i in range(1, num_labels):  # 0 est l'arrière-plan
            x, y, w, h, area = stats[i]
            if float(area)/float(page_height*page_width) < areamin :
                continue  # ignore petites composantes
                
            components.append({
                "id" : f"0_{i}",       # CC sont children de page 
                "parent" : "0",        # CC sont children de page 
                "label": new_label,
                "x": int(x),
                "y": int(y),
                "width": int(w),
                "height": int(h),                
            })

        print(f"==> Detected {len(components)} connected components.")
        return components
