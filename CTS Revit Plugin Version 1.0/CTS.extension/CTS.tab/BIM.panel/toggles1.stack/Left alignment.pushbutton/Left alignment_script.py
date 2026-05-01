# -*- coding: utf-8 -*-
__title__ = "Left alignment"
__doc__ = """Version 1.0  

How to use:

- Select tags in the view
- Run the command to align all tags to the lefttmost one

Author: Bruno Dias"""

__author__ = "Bruno Dias"
__min_revit_ver__ = 2024
__max_revit_ver__ = 2025


###### imports ########

import os
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import *
from pyrevit import forms, revit, script

import clr
clr.AddReference('System')
from System.Collections.Generic import List


###### Variables ########

doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
app = __revit__.Application
active_view = doc.ActiveView


###### Functions ########

def select_tags():
    
    allowed_cats = {
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
    }

    selected_ids = uidoc.Selection.GetElementIds()
    if not selected_ids:
        return None

    filtered = []
    for eid in selected_ids:
        e = doc.GetElement(eid)
        if e and e.Category and e.Category.BuiltInCategory in allowed_cats:
            filtered.append(e)

    if not filtered:
        forms.alert("No element recognized in the selection.", title="Tag alignment")
        return None

    return filtered


def get_position(tag):
    return tag.TagHeadPosition


def get_leftmost_tag(tags, view):
    """Retorna a tag mais à esquerda (menor projeção na direção RightDirection)."""
    leftmost = None
    min_proj = float("inf")
    right_dir = view.RightDirection

    for t in tags:
        try:
            pos = get_position(t)
            proj = pos.DotProduct(right_dir)
            if proj < min_proj:
                min_proj = proj
                leftmost = t
        except:
            pass
    return leftmost


def align_tags(reference_tag, tag_list, view, spacing=0.15, elbow_offset=0.02):
    """Alinha tags verticalmente, mantendo o X da referência (esquerda), e ajusta o leader elbow."""
    ref_pos = get_position(reference_tag)
    up_dir = view.UpDirection
    right_dir = view.RightDirection

    above, below = [], []

    for tag in tag_list:
        if tag.Id == reference_tag.Id:
            continue
        pos = get_position(tag)
        if pos.DotProduct(up_dir) > ref_pos.DotProduct(up_dir):
            above.append(tag)
        else:
            below.append(tag)

    above.sort(key=lambda t: abs(get_position(t).DotProduct(up_dir) - ref_pos.DotProduct(up_dir)))
    below.sort(key=lambda t: abs(get_position(t).DotProduct(up_dir) - ref_pos.DotProduct(up_dir)))

    t = Transaction(doc, "Left alignment")
    t.Start()

    for i, tag in enumerate(above):
        pos = get_position(tag)
        offset = (i + 1) * spacing
        new_point = ref_pos + (up_dir.Normalize() * offset)
        tag.TagHeadPosition = XYZ(pos.X, new_point.Y, pos.Z)

        # # Ajuste do leader elbow
        # tagged_ref = tag.TaggedLocalElement.GetReference()
        # direction = right_dir.Normalize()  # quebra horizontal
        # elbow = tag.TagHeadPosition + direction.Multiply(elbow_offset)
        # tag.SetLeaderElbow(tagged_ref, elbow)

    for i, tag in enumerate(below):
        pos = get_position(tag)
        offset = -(i + 1) * spacing
        new_point = ref_pos + (up_dir.Normalize() * offset)
        tag.TagHeadPosition = XYZ(pos.X, new_point.Y, pos.Z)

        # # Ajuste do leader elbow
        # tagged_ref = tag.TaggedLocalElement.GetReference()
        # direction = right_dir.Normalize()  # quebra horizontal
        # elbow = tag.TagHeadPosition + direction.Multiply(elbow_offset)
        # tag.SetLeaderElbow(tagged_ref, elbow)

    t.Commit()


###### Main ########
allowed_views = [ViewType.CeilingPlan, ViewType.FloorPlan, ViewType.Elevation, ViewType.Section]
if active_view.ViewType in allowed_views:
    
    tags = select_tags()
    if tags:
        ref_tag = get_leftmost_tag(tags, active_view)
        if ref_tag:
            align_tags(ref_tag, tags, active_view, spacing=2.0)
