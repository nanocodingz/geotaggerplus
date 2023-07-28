import arcpy                #geotaggerplus tool for DJI photo that has shitty data structure
import arcpy.da             #worked with photo taken by DJI P4Pro camera, for other DJI products IDK maybe
import os.path as oph       #First and last version by Nano because I am too lazy

class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "geotaggerplus"
        self.alias = "geotagger compatible with DJI photos"

        # List of tool classes associated with this toolbox
        self.tools = [Tool]

class Tool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "geotaggerplus"
        self.description = "geotagger but for DJI photos"
        self.canRunInBackground = False

    def getParameterInfo(self):
        # 放圖片的資料夾路徑
        folder = arcpy.Parameter(
            displayName="Input Folder",
            name="in_features",
            datatype="DEFolder",
            parameterType="Required",
            direction="Input")

        # 輸出的位置
        target = arcpy.Parameter(
            displayName="Output Feature Class",
            name="sinuosity_field",
            datatype="DEFeatureClass",
            parameterType="Required",
            direction="None")

        pram = [folder, target]
        return pram

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, pram):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        pram[0].value = oph.join(pram[0].valueAsText)
        pram[1].value = oph.join(pram[1].valueAsText)
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def getval(self,path,imgname,tagtarget):
        b = b"\x3c\x2f\x72\x64\x66\x3a\x44\x65\x73\x63\x72\x69\x70\x74\x69\x6f\x6e\x3e" #binary tag['<rdf:Description ']
        a = b"\x3c\x72\x64\x66\x3a\x44\x65\x73\x63\x72\x69\x70\x74\x69\x6f\x6e\x20"     #binary tag['</rdf:Description>']

        target = bytearray()
        target.extend(map(ord, tagtarget))  #convert taget tag into binary
        img = open(path + "\\" + imgname, 'rb')  #rb = read binary
        flag = False
        for i in img.readlines():
            if a in i:
                flag = True
            if flag:
                #data += i
                if target in i:
                    val = str(i.decode('ascii'))
                    val = float(val[val.index('"')+1:-2])
                    if val < 0:
                        return (360 + val)
                    else:
                        return val
            if b in i:
                break
        #data = str(data.decode('ascii'))

    def IOconverter(self, pram):
        return pram[0].valueAsText, pram[1].valueAsText

    def feature_editor(self,imgpath,target):
        workspace = oph.dirname(target)
        edit = arcpy.da.Editor(workspace)
        edit.startEditing(with_undo=False, multiuser_mode=True)
        edit.startOperation()
        fields = ['Name','Direction']
        with arcpy.da.UpdateCursor(target, fields) as cursor:
            for row in cursor:
                row[1] = self.getval(imgpath,row[0],"GimbalYawDegree") #row[0] = filename
                cursor.updateRow(row)
        edit.stopOperation()
        edit.stopEditing(save_changes=True)

    def execute(self, pram, messages):
        folder, outlet = self.IOconverter(pram)
        arcpy.GeoTaggedPhotosToPoints_management(folder, outlet, "", "", "ADD_ATTACHMENTS")
        self.feature_editor(folder, outlet)
        return

    def postExecute(self, pram):
        """This method takes place after outputs are processed and
        added to the display."""
        return