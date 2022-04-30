#version 410
layout(points) in;
layout(triangle_strip, max_vertices = 60) out;

uniform float z_near = -1;
uniform vec2 position = vec2( 0, 0);


void main()
{
    vec4 position_2 = gl_in[0].gl_Position;

    gl_Position = vec4( 0.1, 0.1, 0., 1.)+vec4(position*2, z_near, 0)+position_2;
    EmitVertex();

    gl_Position = vec4( 0.1, -0.1, 0., 1.)+vec4(position*2, z_near, 0)+position_2;
    EmitVertex();

    gl_Position = vec4( -0.1, -0.1, 0., 1.)+vec4(position*2, z_near, 0)+position_2;
    EmitVertex();

    gl_Position = vec4( -0.1, 0.1, 0., 1.)+vec4(position*2, z_near, 0)+position_2;
    EmitVertex();

    EndPrimitive();

}