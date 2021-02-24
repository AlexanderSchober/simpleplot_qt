#version 410

in vec4 texture_coordinate;
out vec4 fragment_color;
uniform vec4 label_color = vec4(0,1,0,1);
uniform sampler2D label_texture;

in vec4 texture_coords;
in vec2 center_pixel_position;
in mat2 texture_rotation;

void main() {
    vec2 fragment_position = texture_rotation*(gl_FragCoord.xy - center_pixel_position);
    vec2 texture_pos = vec2(
        (texture_coords.x + fragment_position.x) * texture_coords.b,
        (texture_coords.y - fragment_position.y) * texture_coords.a
    );
    fragment_color = vec4(
        label_color.rgb,
        texture(label_texture, vec2(texture_pos.x, texture_pos.y)).r * label_color.a
    );
}
