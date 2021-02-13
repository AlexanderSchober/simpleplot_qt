#version 410
layout(points) in;
layout(triangle_strip, max_vertices = 1600) out;

uniform float z_near = -1;
uniform float char_index[400];
uniform float position_row_title[400];
uniform float positions_width_title[400];
uniform float char_width_title[400];
uniform float limit;
uniform float height;
uniform float factor;
uniform vec2 viewport_size;

out vec2 texture_coords;
out vec2 center_position;

float startOffset(float viewport_pixel_size)
{
    float width = 0;
    for (int i = 0; i < int(limit); ++i){
        width += factor * char_width_title[int(char_index[i])] * viewport_pixel_size;
    }
    return width / 2.;
}

void main()
{
    // get the points
    vec3 position = gl_in[0].gl_Position.xyz;
    vec2 viewport_pixel_size = 2 / viewport_size;
    float height_in_coords = height * viewport_pixel_size.y;
    float start_offset = startOffset(viewport_pixel_size.x);

    vec2 current_pos = vec2(position.x - start_offset, position.y);
    for (int i = 0; i < int(limit); ++i){

        texture_coords = vec2(positions_width_title[i] + char_width_title[int(char_index[i])] / 2, position_row_title[i] +  / 2);
        center_position = vec2(current_pos.x + factor * char_width_title[int(char_index[i])] * viewport_pixel_size.x /2, current_pos.y );

        width += factor * char_width_title[int(char_index[i])];
        color_vertex = axis_color;
        gl_Position = vec4(positions[0].xy, z_near, 1);
        EmitVertex();
        gl_Position = vec4((positions[1]-perp_dir*axis_thickeness/2).xy, z_near, 1);
        EmitVertex();
        gl_Position = vec4((positions[0]+perp_dir*axis_thickeness/2).xy, z_near, 1);
        EmitVertex();
        gl_Position = vec4((positions[1]+perp_dir*axis_thickeness/2).xy, z_near, 1);
        EmitVertex();
        EndPrimitive();
    }
}