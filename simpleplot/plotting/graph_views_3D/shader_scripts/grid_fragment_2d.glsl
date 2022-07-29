#version 400

uniform sampler2D grid_texture;
uniform vec4 grid_color=vec4(0,0,1,1);

in vec2 texture_position;
out vec4 fragment_color;

void main() {
    float i = texture(grid_texture, texture_position).x;
    fragment_color = grid_color*i;
}

