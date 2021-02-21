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
uniform float rotation = 45;

out vec4 texture_coords;
out vec2 center_pixel_position;

void main()
{
    // Get the width of the text
    float width_pixel = 0.;
    for (int i = 0; i < int(limit); ++i){
        float char_index = 1000.*float(texture(char_index_title, vec2((i+0.5)/(limit), 0.5)).r);
        float char_width = 1000.*float(texture(char_width_title, vec2((char_index+0.5)/title_texture_len, 0.5)).r);
        width_pixel += float(char_width);
    }

    // Pixel size
    vec2 viewport_pixel_size = 2. / viewport_size;
    float height_scene = height * viewport_pixel_size.y;

    // Get the points
    vec2 rotation_position;
    float rotation_angle = (rotation / 180) * 3.145;
    mat2 roation_mat = mat2(cos(rotation_angle), sin(rotation_angle), - sin(rotation_angle), cos(rotation_angle));
    vec3 position = gl_in[0].gl_Position.xyz;
    vec2 current_pos = vec2(position.x - (width_pixel/2)*viewport_pixel_size.x, position.y);
    for (int i = 0; i < int(limit); ++i){

        float char_index = 1000.*float(texture(char_index_title, vec2((float(i)+0.5)/limit, 0.5)).r);
        float char_width = 1000.*float(texture(char_width_title, vec2((char_index+0.5)/title_texture_len, 0.5)).r);
        float position_row = 1000.*float(texture(positions_rows_title, vec2((char_index+0.5)/title_texture_len, 0.5)).r);
        float position_width = 1000.*float(texture(positions_width_title, vec2((char_index+0.5)/title_texture_len, 0.5)).r);

        texture_coords = vec4(
            position_width + char_width/2,
            position_row + height/2,
            factor.y,factor.x
        );

        vec2 center_position = vec2(
            current_pos.x + (char_width/2.) * viewport_pixel_size.x,
            current_pos.y
        );

        center_pixel_position = vec2(
            (center_position.x + 1.)/2. * viewport_size.x,
            (center_position.y + 1.)/2. * viewport_size.y
        );


        rotation_position = roation_mat * (vec2(center_position.x - (char_width/2.)*viewport_pixel_size.x,center_position.y - height_scene/2) - position.xy) + position.xy;
        gl_Position = vec4(rotation_position,-1,1);
        EmitVertex();

        rotation_position = roation_mat * (vec2(center_position.x + (char_width/2.)*viewport_pixel_size.x,center_position.y - height_scene/2) - position.xy) + position.xy;
        gl_Position = vec4(rotation_position,-1,1);
        EmitVertex();

        rotation_position = roation_mat * (vec2(center_position.x - (char_width/2.)*viewport_pixel_size.x,center_position.y + height_scene/2) - position.xy) + position.xy;
        gl_Position = vec4(rotation_position,-1,1);
        EmitVertex();

        rotation_position = roation_mat * (vec2(center_position.x + (char_width/2.)*viewport_pixel_size.x,center_position.y + height_scene/2) - position.xy) + position.xy;
        gl_Position = vec4(rotation_position,-1,1);
        EmitVertex();

        EndPrimitive();

        current_pos = vec2(
            current_pos.x + (char_width * viewport_pixel_size.x)+0.01,
            current_pos.y
        );
    }
}