#version 400

uniform vec4 grid_color;
out vec4 fragment_color;

void main() {
    fragment_color = grid_color;
}

