# -*- coding: utf-8 -*-
__title__ = "Right alignment"
__doc__ = """How to use:
 
- Select tags in the view
- Run the command to align all tags to the rightmost one

Author: Bruno Dias
"""

__author__ = "Bruno Dias"
__min_revit_ver__ = 2023
__max_revit_ver__ = 2026


###### imports ########

from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import *
from pyrevit import forms
import clr
clr.AddReference('System')


###### Variables ########

doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
active_view = doc.ActiveView



###### Helper: detectar eixo horizontal ######

def get_horizontal_axis(view):
    """
    Descobre qual eixo do mundo (X,Y,Z) representa o eixo horizontal da vista.
    """
    rd = view.RightDirection
    abs_vals = [abs(rd.X), abs(rd.Y), abs(rd.Z)]
    max_index = abs_vals.index(max(abs_vals))
    return ["X", "Y", "Z"][max_index]


###### Seleção ######

def select_tags():

    allowed = {
        BuiltInCategory.OST_FabricationPipeworkTags,
        BuiltInCategory.OST_WallTags,
        BuiltInCategory.OST_FabricationHangerTags,
        BuiltInCategory.OST_PipeAccessoryTags,
        BuiltInCategory.OST_PipeTags,
        BuiltInCategory.OST_DoorTags,
        BuiltInCategory.OST_FloorTags,
        BuiltInCategory.OST_WindowTags,
        BuiltInCategory.OST_AreaTags,
        BuiltInCategory.OST_FlexPipeTags,
        BuiltInCategory.OST_FurnitureTags,
        BuiltInCategory.OST_RoofTags,
        BuiltInCategory.OST_PipeFittingTags,
        BuiltInCategory.OST_MechanicalEquipmentTags,
        BuiltInCategory.OST_StructuralFramingTags,

    }

    selected_ids = uidoc.Selection.GetElementIds()
    if not selected_ids:
        return None

    filtered = []
    for eid in selected_ids:
        e = doc.GetElement(eid)
        if e and e.Category and e.Category.BuiltInCategory in allowed:
            filtered.append(e)

    if not filtered:
        forms.alert("No element recognized in the selection.", title="Tag alignment")
        return None

    return filtered



###### Função principal para achar o RIGHTMOST ######

def get_rightmost_tag(tags, view):

    axis = get_horizontal_axis(view)
    rd = view.RightDirection

    # Detecta se valores maiores vão para a direita ou esquerda da vista
    direction = getattr(rd, axis)

    # Se direction > 0 → maior valor = direita
    # Se direction < 0 → menor valor = direita (invertido)
    looking_for_max = direction > 0

    best_tag = None
    best_value = None

    for t in tags:
        try:
            pos = t.TagHeadPosition
            val = getattr(pos, axis)

            if best_tag is None:
                best_tag = t
                best_value = val
                continue

            if looking_for_max:
                if val > best_value:
                    best_value = val
                    best_tag = t
            else:
                if val < best_value:
                    best_value = val
                    best_tag = t

        except:
            pass

    return best_tag



###### Alinhamento ######

def align_tags(reference_tag, tag_list):
    """Move somente no eixo horizontal correto e ajusta os Leaders."""

    axis = get_horizontal_axis(active_view)
    ref_pos = reference_tag.TagHeadPosition

    t = Transaction(doc, "Right alignment with Elbow")
    t.Start()

    for tag in tag_list:
        if tag.Id == reference_tag.Id:
            continue

        current_pos = tag.TagHeadPosition
        current_val = getattr(current_pos, axis)
        ref_val = getattr(ref_pos, axis)

        # 1. Calcular o deslocamento (Delta) no eixo horizontal
        if axis == "X":
            delta = XYZ(ref_val - current_val, 0, 0)
        elif axis == "Y":
            delta = XYZ(0, ref_val - current_val, 0)
        else:  # Z
            delta = XYZ(0, 0, ref_val - current_val)

        # 2. Mover a Cabeça da Tag (usando .Add para ser mais limpo)
        tag.TagHeadPosition = current_pos.Add(delta)


    t.Commit()


###### Main ########

allowed_views = [
    ViewType.CeilingPlan,
    ViewType.FloorPlan,
    ViewType.Elevation,
    ViewType.Section
]

if active_view.ViewType in allowed_views:

    tags = select_tags()
    if tags:

        ref_tag = get_rightmost_tag(tags, active_view)

        if ref_tag:
            align_tags(ref_tag, tags)
