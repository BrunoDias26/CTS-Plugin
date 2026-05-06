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

# 6. Ajuste de Size com Verificação de "Pós-Set"
pipe_size_raw = pipe.get_Parameter(BuiltInParameter.RBS_REFERENCE_OVERALLSIZE).AsString()
success_size = False

t_size = Transaction(doc, "Adjust Hanger Size")
t_size.Start()
try:
    size_param = hanger.get_Parameter(BuiltInParameter.FABRICATION_PRODUCT_ENTRY)
    if size_param and pipe_size_raw:
        # Tenta aplicar o tamanho
        size_param.Set(pipe_size_raw)
        
        # VERIFICAÇÃO CRUCIAL: O Revit aplicou exatamente o que pedimos ou arredondou?
        # Se o valor após o Set for diferente do que pedimos, significa que não há match real
        if size_param.AsString() == pipe_size_raw:
            success_size = True
        else:
            # Tenta uma última vez sem aspas, caso o banco de dados use formato limpo
            clean_size = pipe_size_raw.replace('"', '').strip()
            size_param.Set(clean_size)
            if size_param.AsString() == clean_size:
                success_size = True
    
    t_size.Commit()
except:
    t_size.RollBack()

if not success_size:
    forms.alert("Size Mismatch: The Hanger does not have a valid entry for {}. Connection aborted to avoid incorrect sizing.".format(pipe_size_raw), title="Incompatible Size")
    script.exit()

# 7. Geometria e Conexão
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
        ref_conn = None
        for c in pipe_connectors:
            ref_conn = c
            break
            
        if ref_conn:
            dist = ref_conn.Origin.DistanceTo(target_xyz)
            hosted_info.PlaceOnHost(pipe.Id, ref_conn, dist)
    
    t_host.Commit()
    #print("SUCCESS: Connected to Pipe ID {}".format(pipe.Id))

except Exception as ex:
    t_host.RollBack()
    print("Connection Error: {}".format(ex))





    a = FilteredElementCollector()