#version 410
layout(points) in;
layout(triangle_strip, max_vertices = 100) out;

uniform sampler2D positions_rows_title;
uniform sampler2D positions_width_title;
uniform sampler2D char_index_title;
uniform sampler2D char_width_title;

uniform float z_near = -1;
uniform vec2 viewport_size;
uniform float title_texture_len;
uniform float limit;
uniform float height;
uniform vec2 factor;

out vec4 texture_coords;
out vec2 center_pixel_position;

void main()
{
    // Get the width of the text
    float width_pixel = 0;
    for (int i = 0; i < int(limit); ++i){
        int char_index = int(texture(char_index_title, vec2(i/(limit-1), 0)).r);
        int char_width = int(texture(char_width_title, vec2(char_index/title_texture_len, 0)).r);
        width_pixel += char_width;
    }

    // Pixel size
    vec2 viewport_pixel_size = 2 / viewport_size;
    float height_scene = height * viewport_pixel_size.y;

    // Get the points
    vec3 position = gl_in[0].gl_Position.xyz;
    vec2 current_pos = vec2(position.x - (width_pixel/2)*viewport_pixel_size.x, position.y);;
    for (int i = 0; i < int(limit); ++i){

        int char_index = int(texture(char_index_title, vec2(i/(limit-1), 0)).r);
        float char_width = float(texture(char_width_title, vec2(char_index/title_texture_len, 0)).r);
        float position_row = float(texture(positions_rows_title, vec2(char_index/title_texture_len, 0)).r);
        float position_width = float(texture(positions_width_title, vec2(char_index/title_texture_len, 0)).r);

        texture_coords = vec4(
            position_width + char_width / 2,
            position_row + height/ 2,
            factor.y,
            factor.x
        );
        vec2 center_position = vec2(
            current_pos.x + (char_width /2)*viewport_pixel_size.x,
            current_pos.y
        );

        center_pixel_position = vec2(
            (center_position.x + 1)/2 * viewport_size.x,
            (center_position.y + 1)/2 * viewport_size.y
        );

        gl_Position = vec4(center_position.x - (char_width /2)*viewport_pixel_size.x,center_position.y - height_scene/2,-1,1);
        EmitVertex();
        gl_Position = vec4(center_position.x + (char_width /2)*viewport_pixel_size.x,center_position.y - height_scene/2,-1,1);
        EmitVertex();
        gl_Position = vec4(center_position.x - (char_width /2)*viewport_pixel_size.x,center_position.y + height_scene/2,-1,1);
        EmitVertex();
        gl_Position = vec4(center_position.x + (char_width /2)*viewport_pixel_size.x,center_position.y + height_scene/2,-1,1);
        EmitVertex();

        EndPrimitive();

        current_pos = vec2(
            current_pos.x + (char_width * viewport_pixel_size.x),
            current_pos.y
        );
    }
}