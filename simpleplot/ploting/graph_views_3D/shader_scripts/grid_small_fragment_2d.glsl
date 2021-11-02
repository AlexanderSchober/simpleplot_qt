#version 400

uniform sampler2D grid_small_texture;
uniform vec4 small_grid_color=vec4(0,0,1,1);

in vec2 texture_position;
out vec4 fragment_color;

void main() {
    float i = texture(grid_small_texture, texture_position).x;
    fragment_color = small_grid_color*i;
}

