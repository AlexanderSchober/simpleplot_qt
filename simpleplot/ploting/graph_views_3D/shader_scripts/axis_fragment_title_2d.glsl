#version 410

in vec4 texture_coordinate;
out vec4 fragment_color;
uniform vec4 title_color = vec4(0,1,0,1);
uniform sampler2D text_texture;

in vec4 texture_coords;
in vec2 center_pixel_position;

void main() {
    vec2 fragment_position = gl_FragCoord.xy - center_pixel_position;
    vec2 texture_pos = vec2(
        (texture_coords.x + fragment_position.x) * texture_coords.b,
        (texture_coords.y + fragment_position.y) * texture_coords.a
    );
    fragment_color = vec4(
        title_color.rgb,
        texture(text_texture, vec2(texture_pos.y, texture_pos.x)).r
        * title_color.a
    );
}

