__doc__ = """Reverse 'Hook at Start' and 'Hook at End' of the rebar.

Works only when 'Include hooks is Rebar Shape definition' option is disabled."""
__title__ = "Reverse Hook"
__author__ = "Wolinski"
from Autodesk.Revit import DB
from Autodesk.Revit.UI import *
from Autodesk.Revit.DB import *
import clr

clr.AddReference("System.Windows.Forms")
clr.AddReference("Ironpython.Wpf")
from pyrevit import script
import wpf
from System import Windows

doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
view = doc.ActiveView

xaml_file = script.get_bundle_file("warning.xaml")

# move this class to different file
class MyWindow(Windows.Window):
    def __init__(self):
        wpf.LoadComponent(self, xaml_file)


# Get reinforcement settings
settings = DB.Structure.ReinforcementSettings.GetReinforcementSettings(doc)
defines_hooks = settings.RebarShapeDefinesHooks

# Get selected object
selection = [doc.GetElement(x) for x in uidoc.Selection.GetElementIds()]
# If no object is selected prompt user to select
if len(selection) < 1:
    selection = uidoc.Selection.PickObjects(
        Selection.ObjectType.Element, "Choose rebars"
    )
    elements = [doc.GetElement(el_id) for el_id in selection]
else:
    elements = selection
# TODO: Add check if selected objects are rebars

# Handling transactions
tg = TransactionGroup(doc, "ReverseHook")
tg.Start()


def can_reverse(rebar):
    if rebar.IsRebarShapeDriven() and defines_hooks:
        return False
    elif rebar.IsRebarFreeForm:
        return True
    else:
        print("Unknown rebar type")


# TODO: Make this flexible and working for single bars and rebar groups.
# TODO: Add check if RebarShapeDefinesHooks is true or false, if true messagebox user that function will not work.

for rebar in elements:
    if can_reverse(rebar):
        orient0 = rebar.GetHookOrientation(0)
        orient1 = rebar.GetHookOrientation(1)
        left = DB.Structure.RebarHookOrientation.Left
        right = DB.Structure.RebarHookOrientation.Right
        print(orient0)
        print(orient1)
        t = Transaction(doc, "Reverse")
        t.Start()
        if orient0 == right:
            rebar.SetHookOrientation(0, left)
        elif orient0 == left:
            rebar.SetHookOrientation(0, right)
        if orient1 == right:
            rebar.SetHookOrientation(1, left)
        elif orient1 == left:
            rebar.SetHookOrientation(1, right)
        t.Commit()
    else:
        MyWindow().ShowDialog()

tg.Assimilate()