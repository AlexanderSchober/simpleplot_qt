#version 400

uniform vec4 pointer_color=vec4(0,0,1,1);
out vec4 fragment_color;

void main() {
    fragment_color = pointer_color;
}

