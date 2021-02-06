#version 410
layout(lines) in;
layout(triangle_strip, max_vertices = 4) out;

uniform float z_near = -1;

out vec4 color_vertex;

void main()
{
    // get the pointsi
    vec3 positions[2] = vec3[](
        gl_in[0].gl_Position.xyz,
        gl_in[1].gl_Position.xyz
    );

    vec3 perp_dir = normalize(vec3(
        positions[1].y-positions[0].y,
        positions[0].x-positions[1].x,
        0
    ));

    color_vertex = axis_color;
    gl_Position = vec4((positions[0]-perp_dir*axis_thickeness/2).xy, z_near, 1);
    EmitVertex();
    gl_Position = vec4((positions[1]-perp_dir*axis_thickeness/2).xy, z_near, 1);
    EmitVertex();
    gl_Position = vec4((positions[0]+perp_dir*axis_thickeness/2).xy, z_near, 1);
    EmitVertex();
    gl_Position = vec4((positions[1]+perp_dir*axis_thickeness/2).xy, z_near, 1);
    EmitVertex();
    EndPrimitive();
}