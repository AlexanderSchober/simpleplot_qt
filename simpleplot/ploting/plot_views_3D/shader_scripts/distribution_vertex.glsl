#version 400

in vec4 in_vert;
in vec4 in_color;

out float v_radius;
out vec4  v_color_frag;

void main() {
    v_color_frag    = vec4(in_color);
    v_radius        = in_vert.w;
    gl_Position     = vec4(in_vert.xyz, 1.0);
}
