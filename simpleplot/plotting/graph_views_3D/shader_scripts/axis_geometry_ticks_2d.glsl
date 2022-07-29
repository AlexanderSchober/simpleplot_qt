#version 410
layout(points) in;
layout(triangle_strip, max_vertices = 4) out;

uniform float tick_length;
uniform float small_ticks;
uniform vec3 tick_direction;
uniform vec4 tick_color;
uniform float tick_thickness;
uniform float z_near = -0.991;

out vec4 color_vertex;

void main()
{
    vec3 positions[2] = vec3[](
        gl_in[0].gl_Position.xyz,
        gl_in[0].gl_Position.xyz + tick_length * tick_direction
    );

    vec3 perp_dir = normalize(vec3(
        positions[1].y-positions[0].y,
        positions[0].x-positions[1].x,
        0
    ));

    color_vertex = tick_color;
    gl_Position = vec4((positions[0]-perp_dir*tick_thickness/2).xy, z_near, 1);
    EmitVertex();
    gl_Position = vec4((positions[1]-perp_dir*tick_thickness/2).xy, z_near, 1);
    EmitVertex();
    gl_Position = vec4((positions[0]+perp_dir*tick_thickness/2).xy, z_near, 1);
    EmitVertex();
    gl_Position = vec4((positions[1]+perp_dir*tick_thickness/2).xy, z_near, 1);
    EmitVertex();
    EndPrimitive();

}