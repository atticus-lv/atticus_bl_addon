bl_info = {
    "name": "Save Incremental",
    "author": "Atticus",
    "version": (0,1),
    "blender": (3,0),
    "location": "File > Save Incremental",
    "description": "Save Incremental",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "System",
}

from re import T
import bpy
import shutil
from pathlib import Path
from bpy.types import AddonPreferences
from bpy.app.handlers import persistent


def get_pref():
    return bpy.context.preferences.addons[__name__].preferences

class SaveIncrementalPreferences(AddonPreferences):
    bl_idname = __name__

    type: bpy.props.EnumProperty(name = 'Type',items=[('COPY','Copy',''),('MOVE','Move','')],default='MOVE')
    filepath: bpy.props.StringProperty(name = "File Path", default = "//backup/{filename}_bak{version}.blend")

    def draw(self, context):
        layout = self.layout
        row = layout.row(align = True)
        row.use_property_split = True

        row.prop(self, "type",expand = True)
        layout.prop(self, "filepath")

def get_filepath():
    path_raw = get_pref().filepath
    blend_path = Path(bpy.data.filepath)

    filename = blend_path.stem
    version = bpy.context.scene.save_incremental_count
    path = bpy.path.abspath(path_raw.format(filename=filename, version=version))
    
    dirname = Path(path).parent
    if not dirname.exists():
        dirname.mkdir(parents=True)

    return path 

@persistent
def save_incremental(dummy):
    
    if bpy.data.filepath != '':
        print("save_incremental")

        if bpy.context.preferences.filepaths.save_version == 0:
            bpy.context.preferences.filepaths.save_version = 1
        
        # copy file to backup folder and rename 
        ori_file = bpy.data.filepath+'1'
        tg_file = get_filepath()
        if get_pref().type == 'COPY':
            shutil.copy(ori_file,tg_file)
        elif get_pref().type == 'MOVE':
            shutil.move(ori_file,tg_file)        

        bpy.context.scene.save_incremental_count += 1

        print('save version:', bpy.context.scene.save_incremental_count)

def register():
    bpy.utils.register_class(SaveIncrementalPreferences)
    bpy.types.Scene.save_incremental_count = bpy.props.IntProperty(name="Save Incremental Count", default=0,min = 0)
    bpy.app.handlers.save_post.append(save_incremental)

def unregister():
    bpy.app.handlers.save_post.remove(save_incremental)
    bpy.utils.unregister_class(SaveIncrementalPreferences)
    del bpy.types.Scene.save_incremental_count
