"""
@file delete.py
@brief Règle pour supprimer des objets selon leur label.
"""

from .base import BaseRule


class DeleteRule(BaseRule):
    """
    @class DeleteRule
    @brief Supprime les objets correspondant à un label donné. Actuellement on change just le label "DELETED"
    """     
    def apply(self, bboxes, page_width, page_height):
        #return [box for box in bboxes if box['label'] != self.params['label']]
        for box in bboxes:
            if box['label'] == self.params['label'] :            
                print(f"==> success on {box['label']} => {self.params['new_label']}.")
                box['label'] = self.params['new_label']
                
        return bboxes