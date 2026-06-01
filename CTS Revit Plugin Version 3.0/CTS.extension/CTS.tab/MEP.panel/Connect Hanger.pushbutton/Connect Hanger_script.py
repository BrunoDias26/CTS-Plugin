# -*- coding: utf-8 -*-
__title__ = "Connect Hanger"
__author__ = "Bruno Dias"
__doc__ = """How to use:

- Select 1 Fabrication Hanger and 1 Fabrication Pipe (Straight).
- Run the script command.
- The Hanger will be automatically connected and hosted to the Pipe.

Author: Bruno Dias
"""

from Autodesk.Revit.DB import *
from pyrevit import revit, forms, script

doc = revit.doc
selection = revit.get_selection()

if len(selection) != 2:
    forms.alert("Please select exactly 2 elements.", title="Selection Error")
    script.exit()

hanger = None
pipe = None

# 1. Identificação por Categoria
for el in selection:
    cat_id = el.Category.Id.IntegerValue
    if cat_id == int(BuiltInCategory.OST_FabricationHangers):
        hanger = el
    elif cat_id == int(BuiltInCategory.OST_FabricationPipework):
        pipe = el

# 2. Validação se ambos foram encontrados
if not hanger or not pipe:
    forms.alert("Selection must contain 1 Fabrication Hanger and 1 Fabrication Pipe.", title="Category Mismatch")
    script.exit()

# 3. Validação por Pattern Number (O Pattern 2041 é exclusivo para tubos retos)
pat_param = pipe.get_Parameter(BuiltInParameter.FABRICATION_PART_PAT_NO)
if pat_param and pat_param.AsInteger() != 2041:
    forms.alert("The selected part is not a Straight Pipe.\nPlease select a straight segment.", title="Invalid Fabrication Part")
    script.exit()

# 4. Check de conexão existente
hosted_info = hanger.GetHostedInfo()
if hosted_info and hosted_info.HostId == pipe.Id:
    forms.alert("These elements are already connected.", title="Already Connected")
    script.exit()

# 5. Validação de Service
if hanger.ServiceId != pipe.ServiceId:
    forms.alert("Different Fabrication Services detected.", title="Service Mismatch")
    script.exit()

# 6. Geometria e Conexão (TRECHO MODIFICADO - CONTROLE DE SIZE ENTREGUE AO REVIT)
t_host = Transaction(doc, "Connect Hanger to Pipe")
t_host.Start()
try:
    pipe_curve = pipe.Location.Curve
    bbox = hanger.get_BoundingBox(None)
    h_center = (bbox.Max + bbox.Min) / 2
    
    projection = pipe_curve.Project(h_center)
    target_xyz = projection.XYZPoint
    
    move_vec = XYZ(target_xyz.X - h_center.X, target_xyz.Y - h_center.Y, 0)
    if not move_vec.IsZeroLength():
        ElementTransformUtils.MoveElement(doc, hanger.Id, move_vec)
    
    hosted_info = hanger.GetHostedInfo()
    if hosted_info:
        pipe_connectors = pipe.ConnectorManager.Connectors
        
        # Encontra o conector no início da curva (onde parameter = 0)
        start_point = pipe_curve.GetEndPoint(0)
        ref_conn = None
        
        for c in pipe_connectors:
            if c.Origin.DistanceTo(start_point) < 0.01:
                ref_conn = c
                break
        
        if not ref_conn:
            for c in pipe_connectors:
                ref_conn = c
                break
                
        if ref_conn:
            dist = projection.Parameter
            
            # O PlaceOnHost agora força o Hanger a recalcular seu diâmetro baseado no OD + Insulation do Host
            hosted_info.PlaceOnHost(pipe.Id, ref_conn, dist)
            print("SUCCESS: Connected and automatically sized by Revit!")
    
    t_host.Commit()

except Exception as ex:
    t_host.RollBack()
    print("Connection Error: {}".format(ex))