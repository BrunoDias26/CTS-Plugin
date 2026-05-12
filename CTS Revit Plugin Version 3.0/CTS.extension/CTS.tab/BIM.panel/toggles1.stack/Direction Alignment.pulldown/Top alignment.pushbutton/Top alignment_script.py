# -*- coding: utf-8 -*-
__title__ = "Top alignment"
__doc__ = """How to use:

- Select tags in the view
- Run the command to align all tags to the topmost one

Author: Bruno Dias
"""
__author__ = "Bruno Dias"
__min_revit_ver__ = 2023
__max_revit_ver__ = 2026


from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import *
from pyrevit import forms
import clr
clr.AddReference('System')


doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
active_view = doc.ActiveView


############### Detectar eixo vertical da vista ####################

def get_vertical_axis(view):
    """
    Descobre qual eixo do mundo (X,Y,Z) representa o eixo vertical da vista.
    """
    ud = view.UpDirection
    abs_vals = [abs(ud.X), abs(ud.Y), abs(ud.Z)]
    index = abs_vals.index(max(abs_vals))
    return ["X", "Y", "Z"][index]


############### Seleção de tags ####################

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

    ids = uidoc.Selection.GetElementIds()
    if not ids:
        return None

    result = []
    for eid in ids:
        e = doc.GetElement(eid)
        if e and e.Category and e.Category.BuiltInCategory in allowed:
            result.append(e)

    return result


############### Encontrar o topmost ####################

def get_topmost_tag(tags, view):

    axis = get_vertical_axis(view)
    ud = view.UpDirection

    direction = getattr(ud, axis)

    # Se direction > 0 → maior valor é o top
    # Se direction < 0 → menor valor é o top (invertido)
    looking_for_max = direction > 0

    best_tag = None
    best_value = None

    for t in tags:
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

    return best_tag


############### Alinhamento ####################

def align_tags(reference_tag, tag_list, view):
    axis = get_vertical_axis(view)
    ref_pos = reference_tag.TagHeadPosition

    t = Transaction(doc, "Alinhamento de Tags + Cotovelo")
    t.Start()

    for tag in tag_list:
        if tag.Id == reference_tag.Id:
            continue

        current_pos = tag.TagHeadPosition
        
        # 1. Calcular o deslocamento (Delta)
        if axis == "X":
            delta = XYZ(ref_pos.X - current_pos.X, 0, 0)
        elif axis == "Y":
            delta = XYZ(0, ref_pos.Y - current_pos.Y, 0)
        else: # Z
            delta = XYZ(0, 0, ref_pos.Z - current_pos.Z)

        # 2. Mover a Cabeça da Tag
        tag.TagHeadPosition = current_pos.Add(delta)


    t.Commit()
    
############### Main ####################

allowed_views = [ViewType.CeilingPlan, ViewType.FloorPlan, ViewType.Elevation, ViewType.Section]

if active_view.ViewType in allowed_views:

    tags = select_tags()
    if tags:
        ref = get_topmost_tag(tags, active_view)
        if ref:
            align_tags(ref, tags, active_view)
