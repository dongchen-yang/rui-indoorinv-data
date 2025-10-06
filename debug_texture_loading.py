#!/usr/bin/env python3
"""
Debug script for texture loading issues in Blender-Mitsuba renderer.
This script helps identify and fix common texture loading problems.
"""

import bpy
import bmesh
from pathlib import Path
import numpy as np
from lib.utils_misc import white_blue, blue_text, red, yellow

class TextureDebugger:
    def __init__(self, blend_file_path: Path, xml_file_path: Path):
        self.blend_file_path = blend_file_path
        self.xml_file_path = xml_file_path
        
    def debug_texture_loading(self):
        """
        Main debugging function to check texture loading issues
        """
        print(white_blue("=== Starting Texture Debug Session ==="))
        
        # Step 1: Check if blend file exists and loads correctly
        if not self.blend_file_path.exists():
            print(red(f"ERROR: Blend file not found: {self.blend_file_path}"))
            print(yellow("Solution: You need to manually export the Mitsuba XML to Blender first:"))
            print("1. Open Blender")
            print("2. File -> Import -> Mitsuba (.xml)")
            print(f"3. Select your XML file: {self.xml_file_path}")
            print("4. Save as .blend file")
            return False
            
        # Step 2: Load the blend file
        try:
            bpy.ops.wm.open_mainfile(filepath=str(self.blend_file_path))
            print(blue_text("✓ Blend file loaded successfully"))
        except Exception as e:
            print(red(f"ERROR loading blend file: {e}"))
            return False
            
        # Step 3: Check materials and textures
        self.check_materials_and_textures()
        
        # Step 4: Check texture file paths
        self.check_texture_file_paths()
        
        # Step 5: Check material nodes
        self.check_material_nodes()
        
        # Step 6: Check if textures are properly connected
        self.check_texture_connections()
        
        print(white_blue("=== Debug Session Complete ==="))
        return True
        
    def check_materials_and_textures(self):
        """Check if materials and textures are present in the scene"""
        print(white_blue("\n--- Checking Materials & Textures ---"))
        
        # Check materials
        materials = bpy.data.materials
        print(f"Found {len(materials)} materials:")
        for i, mat in enumerate(materials):
            print(f"  {i+1}. {mat.name}")
            
        # Check textures
        textures = bpy.data.textures
        print(f"Found {len(textures)} textures:")
        for i, tex in enumerate(textures):
            print(f"  {i+1}. {tex.name} (type: {tex.type})")
            
        # Check images
        images = bpy.data.images
        print(f"Found {len(images)} images:")
        for i, img in enumerate(images):
            print(f"  {i+1}. {img.name} (filepath: {img.filepath})")
            if img.filepath:
                img_path = Path(img.filepath)
                if img_path.exists():
                    print(f"    ✓ Image file exists")
                else:
                    print(red(f"    ✗ Image file missing: {img_path}"))
                    
    def check_texture_file_paths(self):
        """Check if texture file paths are correct and accessible"""
        print(white_blue("\n--- Checking Texture File Paths ---"))
        
        missing_textures = []
        for img in bpy.data.images:
            if img.filepath and img.filepath != "":
                img_path = Path(img.filepath)
                if not img_path.exists():
                    missing_textures.append((img.name, img_path))
                    print(red(f"✗ Missing texture: {img.name} -> {img_path}"))
                else:
                    print(f"✓ Found texture: {img.name}")
                    
        if missing_textures:
            print(yellow("\nSuggested fixes for missing textures:"))
            print("1. Check if texture files exist relative to the XML file location")
            print("2. Update texture paths in the original Mitsuba XML")
            print("3. Re-export the XML to Blender")
            print("4. Or manually fix paths in Blender and re-save")
            
        return missing_textures
        
    def check_material_nodes(self):
        """Check material node setups"""
        print(white_blue("\n--- Checking Material Nodes ---"))
        
        for mat in bpy.data.materials:
            print(f"\nMaterial: {mat.name}")
            
            if not mat.use_nodes:
                print(red(f"  ✗ Material {mat.name} not using nodes"))
                continue
                
            tree = mat.node_tree
            if not tree:
                print(red(f"  ✗ No node tree for material {mat.name}"))
                continue
                
            # Check for common nodes
            bsdf_nodes = [n for n in tree.nodes if 'Bsdf' in n.bl_idname]
            tex_nodes = [n for n in tree.nodes if 'Tex' in n.bl_idname]
            img_nodes = [n for n in tree.nodes if n.type == 'TEX_IMAGE']
            
            print(f"  BSDF nodes: {len(bsdf_nodes)}")
            print(f"  Texture nodes: {len(tex_nodes)}")
            print(f"  Image nodes: {len(img_nodes)}")
            
            # Check image nodes specifically
            for img_node in img_nodes:
                if img_node.image:
                    print(f"    Image node: {img_node.name} -> {img_node.image.name}")
                    if not Path(img_node.image.filepath).exists():
                        print(red(f"      ✗ Image file missing"))
                else:
                    print(red(f"    ✗ Image node {img_node.name} has no image assigned"))
                    
    def check_texture_connections(self):
        """Check if textures are properly connected to material outputs"""
        print(white_blue("\n--- Checking Texture Connections ---"))
        
        for mat in bpy.data.materials:
            if not mat.use_nodes or not mat.node_tree:
                continue
                
            tree = mat.node_tree
            output_node = None
            
            # Find material output node
            for node in tree.nodes:
                if node.type == 'OUTPUT_MATERIAL':
                    output_node = node
                    break
                    
            if not output_node:
                print(red(f"  ✗ No material output node found in {mat.name}"))
                continue
                
            # Check connections to output
            surface_input = output_node.inputs.get('Surface')
            if surface_input and surface_input.is_linked:
                connected_node = surface_input.links[0].from_node
                print(f"  Material {mat.name} surface connected to: {connected_node.name}")
                
                # Check if connected node has texture inputs
                self.check_node_texture_inputs(connected_node, mat.name)
            else:
                print(red(f"  ✗ Material {mat.name} surface not connected"))
                
    def check_node_texture_inputs(self, node, mat_name):
        """Check texture inputs for a specific node"""
        texture_inputs = ['Base Color', 'Color', 'Roughness', 'Metallic', 'Normal']
        
        for input_name in texture_inputs:
            if input_name in node.inputs:
                input_socket = node.inputs[input_name]
                if input_socket.is_linked:
                    from_node = input_socket.links[0].from_node
                    if from_node.type == 'TEX_IMAGE':
                        if from_node.image:
                            print(f"    {input_name} connected to image: {from_node.image.name}")
                        else:
                            print(red(f"    ✗ {input_name} image node has no image"))
                    else:
                        print(f"    {input_name} connected to: {from_node.type}")
                else:
                    print(f"    {input_name}: using default value")
                    
    def fix_common_issues(self):
        """Apply common fixes for texture loading issues"""
        print(white_blue("\n--- Applying Common Fixes ---"))
        
        # Fix 1: Ensure all materials use nodes
        for mat in bpy.data.materials:
            if not mat.use_nodes:
                mat.use_nodes = True
                print(f"✓ Enabled nodes for material: {mat.name}")
                
        # Fix 2: Try to reload missing images
        missing_fixed = 0
        for img in bpy.data.images:
            if img.filepath and not Path(img.filepath).exists():
                # Try to find image relative to XML file
                xml_dir = self.xml_file_path.parent
                img_name = Path(img.filepath).name
                potential_path = xml_dir / img_name
                
                if potential_path.exists():
                    img.filepath = str(potential_path)
                    img.reload()
                    print(f"✓ Fixed path for image: {img.name}")
                    missing_fixed += 1
                    
        print(f"Fixed {missing_fixed} missing texture paths")
        
        # Fix 3: Save the corrected blend file
        try:
            bpy.ops.wm.save_mainfile()
            print("✓ Saved corrected blend file")
        except Exception as e:
            print(red(f"Failed to save blend file: {e}"))

def run_texture_debug(scene_name: str, xml_file_path: str):
    """
    Run texture debugging for a specific scene
    
    Args:
        scene_name: Name of the scene
        xml_file_path: Path to the XML file
    """
    xml_path = Path(xml_file_path)
    blend_path = Path(str(xml_path).replace('.xml', '.blend'))
    
    debugger = TextureDebugger(blend_path, xml_path)
    
    success = debugger.debug_texture_loading()
    
    if success:
        # Offer to apply fixes
        response = input("\nApply common fixes? (y/n): ")
        if response.lower() == 'y':
            debugger.fix_common_issues()
    
    return success

if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python debug_texture_loading.py <path_to_xml_file>")
        sys.exit(1)
        
    xml_file_path = sys.argv[1]
    run_texture_debug("debug_scene", xml_file_path) 