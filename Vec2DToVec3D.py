from paraview.util.vtkAlgorithm import *
from vtkmodules.vtkCommonDataModel import vtkUnstructuredGrid
from vtkmodules.vtkCommonCore import vtkDoubleArray, vtkPoints
from vtkmodules.vtkFiltersCore import vtkAppendFilter

@smproxy.filter(label="2D Field to 3D Vector Filter")
@smproperty.input(name="Input", port_index=0)
@smdomain.datatype(dataTypes=["vtkUnstructuredGrid"], composite_data_supported=False)
class Convert2DFieldTo3DVector(VTKPythonAlgorithmBase):
    
    def __init__(self):
        VTKPythonAlgorithmBase.__init__(self,
            nInputPorts=1, nOutputPorts=1, outputType='vtkUnstructuredGrid')
        
        self._vector_name = "VecVel"
        self._field_name = "Vel"
        self._default_z_value = 0.0
    
    @smproperty.stringvector(name="FieldName")
    def SetFieldName(self, name):
        self._field_name = name
        self.Modified()
    
    @smproperty.stringvector(name="OutputVectorName", default_values="ConvertedVector")
    def SetOutputVectorName(self, name):
        self._vector_name = name
        self.Modified()
    
    @smproperty.doublevector(name="DefaultZValue", default_values=0.0)
    def SetDefaultZValue(self, value):
        self._default_z_value = value
        self.Modified()
    
    def FillInputPortInformation(self, port, info):
        info.Set(self.INPUT_REQUIRED_DATA_TYPE(), 'vtkUnstructuredGrid')
        return 1
    
    def RequestData(self, request, inInfo, outInfo):
        input_data = vtkUnstructuredGrid.GetData(inInfo[0])
        output_data = vtkUnstructuredGrid.GetData(outInfo)
        
        if not input_data:
            print("Error: No Input Data")
            return 0
        
        output_data.ShallowCopy(input_data)
        
        if not self._field_name:
            print("Warning: No File Data")
            return 1

        PointData = input_data.GetPointData()
        target_array = None
        
        for i in range(PointData.GetNumberOfArrays()):
            array = PointData.GetArray(i)
            if array and array.GetName() == self._field_name:
                target_array = array
                break
        
        if not target_array:
            print(f"Error: No '{self._field_name}' Data")
            return 0
        
        num_components = target_array.GetNumberOfComponents()
        if num_components != 2:
            print(f"Error: Data '{self._field_name}' Has {num_components} Elements，But Need 2 Element")
            return 0
        
        num_tuples = target_array.GetNumberOfTuples()
        if num_tuples == 0:
            print("Warrning: Empty Data")
            return 1
        
        vector_array = vtkDoubleArray()
        vector_array.SetName(self._vector_name)
        vector_array.SetNumberOfComponents(3)
        vector_array.SetNumberOfTuples(num_tuples)
        
        for i in range(num_tuples):
            x = target_array.GetComponent(i, 0)
            y = target_array.GetComponent(i, 1)
            vector_array.SetComponent(i, 0, x)
            vector_array.SetComponent(i, 1, y)
            vector_array.SetComponent(i, 2, self._default_z_value)
        
        output_data.GetPointData().AddArray(vector_array)
        
        print(f"Successfully '{self._field_name}' To '{self._vector_name}'")
        
        return 1

def _create_plugin_function():
    pass
