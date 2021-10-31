#version 400

uniform vec4 edge_color = vec4(1,1,1,1);
out vec4 fragment_color;

void main() {
    fragment_color = edge_color;
}

