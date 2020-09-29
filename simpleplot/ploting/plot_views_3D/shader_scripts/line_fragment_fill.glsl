#version 400

in vec4 color_vertex;
out vec4 fragment_color;

void main() {
    fragment_color = color_vertex;
}
