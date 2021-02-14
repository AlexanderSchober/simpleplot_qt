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
uniform vec2 factor;
uniform vec2 viewport_size;

out vec2 texture_coords;
out vec2 center_position;

void main()
{
    // Get the width of the text
    float width_pixel = 0;
    for (int i = 0; i < int(limit); ++i){
        width += factor * char_width_title[int(char_index[i])];
    }

    // Pixel size
    vec2 viewport_pixel_size = 2 / viewport_size;
    width_scene = width_pixel * viewport_pixel_size[0];
    height_scene = height * viewport_pixel_size[1];

    // Get the points
    vec3 position = gl_in[0].gl_Position.xyz;
    vec2 current_pos = vec2(position.x - start_offset, position.y);
    for (int i = 0; i < int(limit); ++i){

        texture_coords = vec2(
            (positions_width_title[i] + char_width_title[int(char_index[i])] / 2) * factor.x,
            (position_row_title[i] + height / 2) * factor.y
        );
        center_position = vec2(
            current_pos.x + (char_width_title[int(char_index[i])] * viewport_pixel_size.x) /2,
            current_pos.y
        );

        width += factor * char_width_title[int(char_index[i])];
        gl_Position = vec4(
            center_position.x - (char_width_title[int(char_index[i])] * viewport_pixel_size.x)/2,
            center_position.y - height_scene/2, z_near, 1);
        EmitVertex();
        gl_Position = vec4(
            center_position.x + (char_width_title[int(char_index[i])] * viewport_pixel_size.x)/2,
            center_position.y - height_scene/2, z_near, 1);
        EmitVertex();
        gl_Position = vec4(
            center_position.x - (char_width_title[int(char_index[i])] * viewport_pixel_size.x)/2,
            center_position.y + height_scene/2, z_near, 1);
        EmitVertex();
        gl_Position = vec4(
            center_position.x + (char_width_title[int(char_index[i])] * viewport_pixel_size.x)/2,
            center_position.y + height_scene/2, z_near, 1);
        EmitVertex();
        EndPrimitive();

        current_pos = vec2(
            current_pos.x + (char_width_title[int(char_index[i])] * viewport_pixel_size.x),
            current_pos_y
        );
    }
}