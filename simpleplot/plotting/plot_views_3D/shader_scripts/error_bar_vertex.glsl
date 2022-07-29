#version 400

in vec4 in_vert;
in vec4 in_color;
in vec2 x_error;
in vec2 y_error;
// in vec2 z_error;

out vec4  v_color_frag;
out vec2  x_error_frag;
out vec2  y_error_frag;
// out vec2  z_error_frag[]; For later

void main() {
    v_color_frag    = vec4(in_color);
    x_error_frag    = vec2(x_error);
    y_error_frag    = vec2(y_error);

    gl_Position = vec4(in_vert);
}
