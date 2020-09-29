#version 400

uniform mat4 u_proj_mat;
uniform mat4 u_view_mat;
uniform vec3 u_view_pos;
uniform mat4 u_model_mat;

uniform vec2 u_light_bool;
uniform vec3 u_light_pos;
uniform vec3 u_light_color;

in vec3 in_vert;
in vec3 in_norm;

out vec3 v_normal;

out float light_active;
out vec3  light_pos;
out vec3  view_pos;
out vec3  frag_pos;
out vec3  light_color;

void main() {
    v_normal        = in_norm;

    light_active    = u_light_bool[0];
    frag_pos        = vec3(in_vert);
    light_pos       = vec3(u_light_pos);
    view_pos        = vec3(u_view_pos);
    light_color     = vec3(u_light_color);
    if (u_light_bool[1]==1){
        light_pos = vec3(u_proj_mat * u_view_mat * u_model_mat * vec4(light_pos, 1.0));
    }
    gl_Position = u_proj_mat * u_view_mat * u_model_mat * vec4(in_vert, 1.0);
}
