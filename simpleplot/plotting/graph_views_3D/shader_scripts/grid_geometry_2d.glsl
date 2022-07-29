#version 410
layout(points) in;
layout(triangle_strip, max_vertices = 4) out;

uniform float grid_length;
uniform float small_ticks;
uniform vec3 grid_direction;
uniform float grid_thickness;
uniform float grid_z=-0.9;
uniform float grid_periodicty_length;

out vec2 texture_position;

void main()
{
    vec3 positions[2] = vec3[](
        gl_in[0].gl_Position.xyz,
        gl_in[0].gl_Position.xyz + grid_length * grid_direction
    );

    vec3 perp_dir = normalize(vec3(
        positions[1].y-positions[0].y,
        positions[0].x-positions[1].x,
        0
    ));

    texture_position = vec2(0, 0);
    gl_Position = vec4((positions[0]-perp_dir*grid_thickness/2.).xy, grid_z, 1);
    EmitVertex();
    texture_position = vec2(grid_length/grid_periodicty_length, 0);
    gl_Position = vec4((positions[1]-perp_dir*grid_thickness/2.).xy, grid_z, 1);
    EmitVertex();
    texture_position = vec2(0, 0);
    gl_Position = vec4((positions[0]+perp_dir*grid_thickness/2.).xy, grid_z, 1);
    EmitVertex();
    texture_position = vec2(grid_length/grid_periodicty_length, 0);
    gl_Position = vec4((positions[1]+perp_dir*grid_thickness/2.).xy, grid_z, 1);
    EmitVertex();

    EndPrimitive();

}