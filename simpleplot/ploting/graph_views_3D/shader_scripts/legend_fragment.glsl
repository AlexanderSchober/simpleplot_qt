#version 400

uniform vec4 legend_color = vec4(0,1,0,1);
uniform sampler3D legend_texture;
uniform float legend_width;
uniform float legend_heigh;

in vec2 texture_coords;
in vec2 center_pixel_position;
out vec4 fragment_color;

void main() {
    vec2 tex_position = vec2(
        (0.5 + (gl_FragCoord.x - center_pixel_position.x)/legend_width),
        (0.5 - (gl_FragCoord.y - center_pixel_position.y)/legend_heigh)
    );

    fragment_color = vec4(
        texture(legend_texture, vec3(0.125, tex_position)).r,
        texture(legend_texture, vec3(0.375, tex_position)).r,
        texture(legend_texture, vec3(0.625, tex_position)).r,
        texture(legend_texture, vec3(0.875, tex_position)).r);//texture(legend_texture, vec3(tex_position, 0.875)).r);
}

