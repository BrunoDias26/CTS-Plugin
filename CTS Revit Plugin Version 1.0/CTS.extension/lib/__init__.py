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
rvt_year = int(app.VersionNumber)
Path_script = os.path.dirname(__file__)



def select_tags():
    allowed_cats = {
        BuiltInCategory.OST_FabricationPipeworkTags,
        BuiltInCategory.OST_WallTags
    }

    # Pega os elementos atualmente selecionados no Revit
    selected_ids = uidoc.Selection.GetElementIds()
    if not selected_ids:
        return None

    # Converte IDs em elementos e filtra direto pelas categorias
    filtered = []
    for eid in selected_ids:
        e = doc.GetElement(eid)
        if e and e.Category and e.Category.BuiltInCategory in allowed_cats:
            filtered.append(e)

    if not filtered:
        forms.alert("No element recognized in the selection.", title="Tag alignment")
        return None

    return filtered
    
