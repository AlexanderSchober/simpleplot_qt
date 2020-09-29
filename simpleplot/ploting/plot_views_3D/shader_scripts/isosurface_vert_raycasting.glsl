#version 410

in vec3 in_vert;

uniform mat4 u_proj_mat;
uniform mat4 u_view_mat;
uniform mat4 u_model_mat;

void main() {
    gl_Position = u_proj_mat * u_view_mat * u_model_mat * vec4(in_vert,1);
}
