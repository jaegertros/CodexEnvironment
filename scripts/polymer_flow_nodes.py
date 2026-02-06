"""Create a basic geometry nodes setup for a polymer flow inside a pipe.

Run inside Blender's scripting workspace:
- Open Blender
- Switch to Scripting
- Paste/Run this script

The script adds a "PolymerFlow" geometry node group on the active object.
"""

import bpy


def ensure_active_object() -> bpy.types.Object:
    obj = bpy.context.active_object
    if obj is None:
        raise RuntimeError("Select or create an object to receive the geometry nodes modifier.")
    return obj


def create_polymer_flow_group() -> bpy.types.NodeTree:
    if "PolymerFlow" in bpy.data.node_groups:
        return bpy.data.node_groups["PolymerFlow"]

    group = bpy.data.node_groups.new("PolymerFlow", "GeometryNodeTree")
    group.is_modifier = True

    # Interface
    group.interface.new_socket(name="Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
    group.interface.new_socket(name="Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")

    # Nodes
    nodes = group.nodes
    links = group.links

    group_input = nodes.new("NodeGroupInput")
    group_output = nodes.new("NodeGroupOutput")

    curve_line = nodes.new("GeometryNodeCurvePrimitiveLine")
    curve_line.inputs[0].default_value = (0.0, 0.0, 0.0)
    curve_line.inputs[1].default_value = (2.0, 0.0, 0.0)

    spline_parameter = nodes.new("GeometryNodeSplineParameter")
    set_curve_radius = nodes.new("GeometryNodeSetCurveRadius")
    map_range_bulge = nodes.new("ShaderNodeMapRange")
    map_range_bulge.clamp = True
    map_range_bulge.inputs[1].default_value = 0.7
    map_range_bulge.inputs[2].default_value = 1.0
    map_range_bulge.inputs[3].default_value = 0.2
    map_range_bulge.inputs[4].default_value = 0.3

    curve_circle = nodes.new("GeometryNodeCurvePrimitiveCircle")
    curve_circle.inputs[4].default_value = 0.02

    curve_to_mesh = nodes.new("GeometryNodeCurveToMesh")

    position = nodes.new("GeometryNodeInputPosition")
    separate_xyz = nodes.new("ShaderNodeSeparateXYZ")
    combine_xy = nodes.new("ShaderNodeCombineXYZ")
    vector_math = nodes.new("ShaderNodeVectorMath")
    vector_math.operation = "LENGTH"

    map_range_tangle = nodes.new("ShaderNodeMapRange")
    map_range_tangle.clamp = True
    map_range_tangle.inputs[1].default_value = 0.0
    map_range_tangle.inputs[2].default_value = 0.35
    map_range_tangle.inputs[3].default_value = 1.0
    map_range_tangle.inputs[4].default_value = 0.0

    noise_texture = nodes.new("ShaderNodeTexNoise")
    noise_texture.inputs[2].default_value = 12.0

    vector_math_center = nodes.new("ShaderNodeVectorMath")
    vector_math_center.operation = "SUBTRACT"
    combine_half = nodes.new("ShaderNodeCombineXYZ")
    combine_half.inputs[0].default_value = 0.5
    combine_half.inputs[1].default_value = 0.5
    combine_half.inputs[2].default_value = 0.5

    vector_math_scale = nodes.new("ShaderNodeVectorMath")
    vector_math_scale.operation = "SCALE"

    set_position = nodes.new("GeometryNodeSetPosition")

    color_ramp = nodes.new("ShaderNodeValToRGB")
    color_ramp.color_ramp.elements[0].position = 0.0
    color_ramp.color_ramp.elements[0].color = (0.1, 0.2, 0.9, 1.0)
    color_ramp.color_ramp.elements[1].position = 1.0
    color_ramp.color_ramp.elements[1].color = (0.9, 0.2, 0.1, 1.0)

    store_color = nodes.new("GeometryNodeStoreNamedAttribute")
    store_color.data_type = "FLOAT_COLOR"
    store_color.domain = "POINT"
    store_color.inputs[2].default_value = "Color"

    # Layout
    group_input.location = (-900, 0)
    curve_line.location = (-700, 100)
    spline_parameter.location = (-700, -100)
    map_range_bulge.location = (-500, -100)
    set_curve_radius.location = (-300, 100)
    curve_circle.location = (-300, -100)
    curve_to_mesh.location = (-100, 100)

    position.location = (-500, -400)
    separate_xyz.location = (-300, -400)
    combine_xy.location = (-100, -400)
    vector_math.location = (100, -400)
    map_range_tangle.location = (300, -400)
    noise_texture.location = (500, -520)
    combine_half.location = (500, -700)
    vector_math_center.location = (700, -520)
    vector_math_scale.location = (900, -520)
    set_position.location = (1100, -200)

    color_ramp.location = (700, -200)
    store_color.location = (1300, -200)
    group_output.location = (1500, 100)

    # Links
    links.new(curve_line.outputs[0], set_curve_radius.inputs[0])
    links.new(spline_parameter.outputs[0], map_range_bulge.inputs[0])
    links.new(map_range_bulge.outputs[0], set_curve_radius.inputs[2])
    links.new(set_curve_radius.outputs[0], curve_to_mesh.inputs[0])
    links.new(curve_circle.outputs[0], curve_to_mesh.inputs[1])

    links.new(position.outputs[0], separate_xyz.inputs[0])
    links.new(separate_xyz.outputs[0], combine_xy.inputs[0])
    links.new(separate_xyz.outputs[1], combine_xy.inputs[1])
    links.new(combine_xy.outputs[0], vector_math.inputs[0])
    links.new(vector_math.outputs[1], map_range_tangle.inputs[0])

    links.new(noise_texture.outputs[1], vector_math_center.inputs[0])
    links.new(combine_half.outputs[0], vector_math_center.inputs[1])
    links.new(vector_math_center.outputs[0], vector_math_scale.inputs[0])
    links.new(map_range_tangle.outputs[0], vector_math_scale.inputs[3])

    links.new(curve_to_mesh.outputs[0], set_position.inputs[0])
    links.new(vector_math_scale.outputs[0], set_position.inputs[3])

    links.new(map_range_tangle.outputs[0], color_ramp.inputs[0])
    links.new(color_ramp.outputs[0], store_color.inputs[3])
    links.new(set_position.outputs[0], store_color.inputs[0])
    links.new(store_color.outputs[0], group_output.inputs[0])

    return group


def add_modifier(obj: bpy.types.Object, group: bpy.types.NodeTree) -> None:
    modifier = obj.modifiers.new("PolymerFlow", "NODES")
    modifier.node_group = group


def main() -> None:
    obj = ensure_active_object()
    group = create_polymer_flow_group()
    add_modifier(obj, group)


if __name__ == "__main__":
    main()
