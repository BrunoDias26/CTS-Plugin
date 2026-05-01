# -*- coding: utf-8 -*-
__title__ = "Bottom alignment"
__doc__ = """How to use:  

- Select tags in the view
- Run the command to align all tags to the bottommost one

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


############### Encontrar o bottommost ####################

def get_bottommost_tag(tags, view):

    axis = get_vertical_axis(view)
    ud = view.UpDirection

    # Detecta se valores menores ou maiores descem na vista
    direction = getattr(ud, axis)

    # Se direction > 0 → menor valor é o bottom
    # Se direction < 0 → maior valor é o bottom (invertido)
    looking_for_min = direction > 0

    best_tag = None
    best_value = None

    for t in tags:
        pos = t.TagHeadPosition
        val = getattr(pos, axis)

        if best_tag is None:
            best_tag = t
            best_value = val
            continue

        if looking_for_min:
            if val < best_value:
                best_value = val
                best_tag = t
        else:
            if val > best_value:
                best_value = val
                best_tag = t

    return best_tag


############### Alinhamento ####################

def align_tags(reference_tag, tag_list, view):
    axis = get_vertical_axis(view)
    ref_pos = reference_tag.TagHeadPosition

    t = Transaction(doc, "Bottom alignment with Elbow")
    t.Start()

    for tag in tag_list:
        if tag.Id == reference_tag.Id:
            continue

        current_pos = tag.TagHeadPosition

        # 1. Calcula o Delta (deslocamento necessário para chegar na altura da referência)
        if axis == "X":
            delta = XYZ(ref_pos.X - current_pos.X, 0, 0)
        elif axis == "Y":
            delta = XYZ(0, ref_pos.Y - current_pos.Y, 0)
        else:  # Z
            delta = XYZ(0, 0, ref_pos.Z - current_pos.Z)

        # 2. Move a cabeça da Tag usando o Delta
        tag.TagHeadPosition = current_pos.Add(delta)

        # 3. Move os cotovelos (elbows) de todas as referências da tag
        if tag.HasLeader:
            # Pega todas as setas (referências) da tag
            refs = tag.GetTaggedReferences()
            for r in refs:
                if tag.HasLeaderElbow(r):
                    old_elbow = tag.GetLeaderElbow(r)
                    # Aplica o mesmo deslocamento vertical ao cotovelo
                    tag.SetLeaderElbow(r, old_elbow.Add(delta))

    t.Commit()

############### Main ####################

allowed_views = [ViewType.CeilingPlan, ViewType.FloorPlan, ViewType.Elevation, ViewType.Section]

if active_view.ViewType in allowed_views:

    tags = select_tags()
    if tags:
        ref = get_bottommost_tag(tags, active_view)
        if ref:
            align_tags(ref, tags, active_view)
