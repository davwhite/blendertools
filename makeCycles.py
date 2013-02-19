import bpy
from mathutils import Vector

def loadFile(fileName):
    matArrays = []
    prevMat = ""
    nextMat = ""
    
    f = open(fileName,'r')
    
    matName = ""
    d = ""
    Ns = ""
    Ni = ""
    Ka = []
    Kd = ""
    Ks = ""
    Km = ""
    map_Kd = ""
    map_D = ""
    
    lineNum = 0
        
    for line in f:
        mHeader = line.split(" ")[0]
        if (mHeader == 'newmtl'):
            matName = line.split(" ")[1].strip()
            currentMat = matName
            
        if (currentMat != prevMat) and (lineNum > 0):
            matArray = [prevMat,d,Ns,Ni,Ka,Kd,Ks,Km,map_Kd,map_D]
            matArrays.append(matArray)
            d = ""
            Ns = ""
            Ni = ""
            Ka = ""
            Kd = ""
            Ks = ""
            Km = ""
            map_Kd = ""
            map_D = ""

        if (mHeader == 'd'):
            d = line.split(" ")[1].strip()
        if (mHeader == 'Ns'):
            Ns = line.split(" ")[1].strip()
        if (mHeader == 'Ni'):
            Ni = line.split(" ")[1].strip()
        if (mHeader == 'Ka'):
            Ka0 = line.split(" ")[1].strip()
            Ka1 = line.split(" ")[2].strip()
            Ka2 = line.split(" ")[3].strip()
            Ka = [Ka0,Ka1,Ka2]
        if (mHeader == 'Kd'):
            Kd0 = line.split(" ")[1].strip()
            Kd1 = line.split(" ")[2].strip()
            Kd2 = line.split(" ")[3].strip()
            Kd = [Kd0,Kd1,Kd2]
        if (mHeader == 'Ks'):
            Ks0 = line.split(" ")[1].strip()
            Ks1 = line.split(" ")[2].strip()
            Ks2 = line.split(" ")[3].strip()
            Ks = [Ks0,Ks1,Ks2]
        if (mHeader == 'Km'):
            Km = line.split(" ")[1].strip()
        if (mHeader == 'map_Kd'):
            map_Kd = line.split(" ")[1].strip()
        if (mHeader == 'map_D'):
            map_D = line.split(" ")[1].strip()
    
            
        prevMat = currentMat
        lineNum += 1
    return matArrays

filPath = 'E://Users/David/Documents/3D/Blender/Urban4'

filName = filPath + '/UrbanFull.mtl'
matArray = loadFile(filName)
texArray = []

for m in matArray:
    mName = m[0]
    mTex = m[8]
    tTex = m[9]
#        print("mName: " + mName + "  mTex: " + mTex)
    my_mat = bpy.data.materials.new(mName)
    my_mat.use_nodes = True
    
    
    nodes = {'Image Texture':['TEX_IMAGE',(-300.0, 0)],'Diffuse BSDF':['BSDF_DIFFUSE',(0, 0)],'Material Output': ['OUTPUT_MATERIAL',(300.0, 0)]}
    if (len(tTex) > 0):
        nodes = {'Image1':['TEX_IMAGE',(-300.0, 0)],'Image2':['TEX_IMAGE',(-600.0, 0)],'Diffuse BSDF':['BSDF_DIFFUSE',(0, 0)],'Transparent BSDF':['BSDF_TRANSPARENT',(0, -300)],'Mix Shader': ['MIX_SHADER', (-600, -300.0)],'Material Output': ['OUTPUT_MATERIAL',(300.0, 0)]}        
     
    for k, v in nodes.items():
        location = Vector(v[1])
        if not k in my_mat.node_tree.nodes:
            cur_node = my_mat.node_tree.nodes.new(v[0])
            cur_node.location = location
        else:
            my_mat.node_tree.nodes[k].location = location
    link00 = ['Image Texture','Color','Diffuse BSDF','Color']
    link01 = ['Diffuse BSDF','BSDF','Material Output','Surface']
    links = [link00]
    
            
    if (len(tTex) > 0) and (len(mTex) > 0):
        from_node = my_mat.node_tree.nodes['Image Texture.001']
        output_socket = from_node.outputs['Color']
        to_node = my_mat.node_tree.nodes['Diffuse BSDF']
        input_socket = to_node.inputs['Color']
        my_mat.node_tree.links.new(output_socket,input_socket)

        nodes = my_mat.node_tree.nodes
        imgName = filPath + mTex
        img = bpy.data.images.load(imgName)
        imageNode = nodes['Image Texture.001']
        imageNode.image = img

        from_node = my_mat.node_tree.nodes['Image Texture']
        output_socket = from_node.outputs['Color']
        to_node = my_mat.node_tree.nodes['Mix Shader']
        input_socket = to_node.inputs['Fac']
        my_mat.node_tree.links.new(output_socket,input_socket)
        nodes = my_mat.node_tree.nodes
        imgName = filPath + tTex
        img = bpy.data.images.load(imgName)
        imageNode = nodes['Image Texture']
        imageNode.image = img
        
        from_node = my_mat.node_tree.nodes['Mix Shader']
        output_socket = from_node.outputs['Shader']
        to_node = my_mat.node_tree.nodes['Material Output']
        input_socket = to_node.inputs['Surface']
        my_mat.node_tree.links.new(output_socket,input_socket)

        from_node = my_mat.node_tree.nodes['Diffuse BSDF']
        output_socket = from_node.outputs['BSDF']
        to_node = my_mat.node_tree.nodes['Mix Shader']
        input_socket = to_node.inputs[2]
        my_mat.node_tree.links.new(output_socket,input_socket)
        
        from_node = my_mat.node_tree.nodes['Transparent BSDF']
        output_socket = from_node.outputs['BSDF']
        to_node = my_mat.node_tree.nodes['Mix Shader']
        input_socket = to_node.inputs[1]
        my_mat.node_tree.links.new(output_socket,input_socket)

        obj = bpy.context.active_object
        for mn in obj.material_slots:
            sName = mn.name
            if (sName == m[0]):
                obj.material_slots[m[0]].material = my_mat
            
        
        print("mName: " + mName + "  tTex: " + tTex)
            
    else:
        if(len(mTex) > 0):
            from_node = my_mat.node_tree.nodes['Image Texture']
            output_socket = from_node.outputs['Color']
            to_node = my_mat.node_tree.nodes['Diffuse BSDF']
            input_socket = to_node.inputs['Color']
            my_mat.node_tree.links.new(output_socket,input_socket)
    
            nodes = my_mat.node_tree.nodes
            imgName = filPath + mTex
            img = bpy.data.images.load(imgName)
            imageNode = nodes['Image Texture']
            imageNode.image = img
            obj = bpy.context.active_object
            for mn in obj.material_slots:
                sName = mn.name
                if (sName == m[0]):
                    obj.material_slots[m[0]].material = my_mat
            
#            print("slotName: " + sName + "  fName: " + mTex)



