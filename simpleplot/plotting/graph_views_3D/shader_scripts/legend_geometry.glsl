#version 410
layout(points) in;
layout(triangle_strip, max_vertices = 10) out;

uniform vec2 viewport_size;

out vec2 texture_coords;
out vec2 center_pixel_position;

void main()
{
    vec4 center = gl_in[0].gl_Position;
    vec2 real_center = vec2(1 - (center.x+center.z)/viewport_size.x, 1 - (center.y+center.a)/viewport_size.y);

    center_pixel_position = (real_center.xy + 1) / 2 * viewport_size;
    texture_coords = vec2(center.z, center.a);

    gl_Position = vec4(real_center.xy + vec2(-center.z/viewport_size.x, center.a/viewport_size.y), -1, 1);
    EmitVertex();
    gl_Position = vec4(real_center.xy + vec2( center.z/viewport_size.x, center.a/viewport_size.y), -1, 1);
    EmitVertex();
    gl_Position = vec4(real_center.xy + vec2(-center.z/viewport_size.x,-center.a/viewport_size.y), -1, 1);
    EmitVertex();
    gl_Position = vec4(real_center.xy + vec2( center.z/viewport_size.x,-center.a/viewport_size.y), -1, 1);
    EmitVertex();

    EndPrimitive();
    
}