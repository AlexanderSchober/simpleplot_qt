#version 410
layout(points) in;
layout(triangle_strip, max_vertices = 60) out;

uniform sampler2D positions_rows_label;
uniform sampler2D positions_width_label;
uniform sampler2D char_index_label;
uniform sampler2D char_width_label;

uniform float z_near = -1;
uniform vec2 viewport_size;

uniform float label_texture_len;
uniform float label_limit;
uniform float label_height;
uniform vec2 label_factor;

uniform float label_angle = 0;
uniform float label_v_just = 0;
uniform float label_h_just = 0;

out vec4 texture_coords;
out vec2 center_pixel_position;
out mat2 texture_rotation;

vec2 rotatePoint(vec2 point_in, vec2 center){
    vec2 point_out;
    float rotation_angle = (label_angle / 180) * 3.145;
    mat2 roation_mat = mat2(cos(rotation_angle), sin(rotation_angle), - sin(rotation_angle), cos(rotation_angle));
    vec2 center_px = (center+1)/2 * viewport_size;
    vec2 point_in_px = (point_in+1)/2 * viewport_size;
    point_out = roation_mat * (point_in_px - center_px) + center_px;
    return (point_out / viewport_size)*2 - 1;
}

void main()
{
    vec4 position = gl_in[0].gl_Position;

    // Get the width of the text
    float width_pixel = 0.;
    for (int i = int(position[2]); i < int(position[3]); ++i){
        float char_index = 1000.*float(texture(char_index_label, vec2((i+0.5)/(label_limit), 0.5)).r);
        float char_width = 1000.*float(texture(char_width_label, vec2((char_index+0.5)/label_texture_len, 0.5)).r);
        width_pixel += float(char_width);
    }

    // Pixel size
    vec2 viewport_pixel_size = 2. / viewport_size;
    float height_scene = label_height * viewport_pixel_size.y;

    // Get the points
    vec2 rotation_position;
    float rotation_angle = (-label_angle / 180) * 3.145;
    texture_rotation = mat2(cos(rotation_angle), sin(rotation_angle), - sin(rotation_angle), cos(rotation_angle));

    float x_pos = position.x;
    if (label_h_just == 0){x_pos -= (width_pixel/2)*viewport_pixel_size.x;};
    if (label_h_just == 2){x_pos -= (width_pixel)*viewport_pixel_size.x;};

    float y_pos = position.y;
    if (label_v_just == 1){y_pos += height_scene/2;};
    if (label_v_just == 2){y_pos -= height_scene/2;};

    vec2 current_pos = vec2(x_pos, y_pos);
    for (int i = int(position[2]); i < int(position[3]); ++i){

        float char_index = 1000.*float(texture(char_index_label, vec2((float(i)+0.5)/label_limit, 0.5)).r);
        float char_width = 1000.*float(texture(char_width_label, vec2((char_index+0.5)/label_texture_len, 0.5)).r);
        float position_row = 1000.*float(texture(positions_rows_label, vec2((char_index+0.5)/label_texture_len, 0.5)).r);
        float position_width = 1000.*float(texture(positions_width_label, vec2((char_index+0.5)/label_texture_len, 0.5)).r);

        texture_coords = vec4(
            position_width + char_width/2,
            position_row + label_height/2,
            label_factor.y,label_factor.x
        );

        vec2 center_position = vec2(
            current_pos.x + (char_width/2.) * viewport_pixel_size.x,
            current_pos.y
        );

        center_pixel_position = (rotatePoint(center_position,position.xy) + 1) / 2 * viewport_size;

        rotation_position = vec2(center_position.x - (char_width/2.)*viewport_pixel_size.x,center_position.y - height_scene/2);
        gl_Position = vec4(rotatePoint(rotation_position, position.xy),-1,1);
        EmitVertex();

        rotation_position = vec2(center_position.x + (char_width/2.)*viewport_pixel_size.x,center_position.y - height_scene/2);
        gl_Position = vec4(rotatePoint(rotation_position, position.xy),-1,1);
        EmitVertex();

        rotation_position = vec2(center_position.x - (char_width/2.)*viewport_pixel_size.x,center_position.y + height_scene/2);
        gl_Position = vec4(rotatePoint(rotation_position, position.xy),-1,1);
        EmitVertex();

        rotation_position = vec2(center_position.x + (char_width/2.)*viewport_pixel_size.x,center_position.y + height_scene/2);
        gl_Position = vec4(rotatePoint(rotation_position, position.xy),-1,1);
        EmitVertex();

        EndPrimitive();

        current_pos = vec2(
            current_pos.x + (char_width * viewport_pixel_size.x)+0.01,
            current_pos.y
        );
    }
}