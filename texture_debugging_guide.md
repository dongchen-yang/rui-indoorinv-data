# Texture Loading Debug Guide

## Step 1: Check if .blend file exists
The renderer expects a `.blend` file that was exported from the Mitsuba XML:

```python
blend_file_path = Path(str(xml_file_path).replace('.xml', '.blend'))
if not blend_file_path.exists():
    print("ERROR: Need to export XML to Blender first!")
```

**Solution**: Open Blender → File → Import → Mitsuba (.xml) → Save as .blend

## Step 2: Check texture file paths
Most texture issues are caused by missing or incorrect file paths:

```python
# Check in Blender Python console
import bpy
for img in bpy.data.images:
    if img.filepath:
        print(f"{img.name}: {img.filepath}")
        print(f"Exists: {Path(img.filepath).exists()}")
```

**Common Issues**:
- Absolute paths that don't exist on your system
- Relative paths that are incorrect
- Missing texture files

## Step 3: Check material node setup
Verify materials are using nodes and have proper connections:

```python
for mat in bpy.data.materials:
    if not mat.use_nodes:
        print(f"Material {mat.name} not using nodes!")
        mat.use_nodes = True  # Fix
```

## Step 4: Test with a simple scene
Create a test scene with known working textures:

```python
# Create a simple test material
mat = bpy.data.materials.new(name="TestMaterial")
mat.use_nodes = True
nodes = mat.node_tree.nodes

# Add image texture node
tex_node = nodes.new(type='ShaderNodeTexImage')
# Load a known existing image
tex_node.image = bpy.data.images.load("/path/to/existing/image.png")
```

## Step 5: Check Blender console for errors
Look for Python errors in Blender's console that might indicate texture loading issues.

## Step 6: Common fixes

### Fix 1: Update texture paths in XML
Edit your Mitsuba XML file to use correct relative paths:

```xml
<!-- Instead of absolute paths -->
<texture type="bitmap" name="albedo">
    <string name="filename" value="/absolute/path/to/texture.png"/>
</texture>

<!-- Use relative paths -->
<texture type="bitmap" name="albedo">
    <string name="filename" value="textures/texture.png"/>
</texture>
```

### Fix 2: Copy textures to correct location
Ensure texture files are in the expected location relative to your XML file.

### Fix 3: Re-export with correct settings
When exporting XML to Blender, ensure:
- All referenced textures exist
- Paths are correctly resolved
- Materials are properly converted

### Fix 4: Manual Blender fixes
In Blender, you can manually:
1. Select problematic materials
2. Go to Shading workspace
3. Check/fix image texture nodes
4. Reassign missing textures
5. Save the .blend file

## Step 7: Test render
After fixes, test with a simple render:

```python
# Quick test render
bpy.context.scene.render.resolution_x = 256
bpy.context.scene.render.resolution_y = 256
bpy.context.scene.cycles.samples = 16
bpy.ops.render.render(write_still=True)
```

## Prevention Tips

1. **Use relative paths** in your Mitsuba XML files
2. **Keep textures organized** in a dedicated folder
3. **Test XML import** in Blender before using with renderer
4. **Version control** your .blend files after successful import
5. **Check file permissions** on texture files 