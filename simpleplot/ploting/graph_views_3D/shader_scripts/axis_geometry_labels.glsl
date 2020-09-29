#version 410
layout(lines) in;
layout(triangle_strip, max_vertices = 34) out;

uniform mat4 u_proj_mat;
uniform mat4 u_view_mat;
uniform mat4 u_model_mat;

uniform vec3 u_view_pos;
uniform vec2 u_light_bool;
uniform vec3 u_light_pos;
uniform vec3 u_light_color;

uniform vec2 axis_length;
uniform vec3 axis_direction;
uniform vec3 axis_center;
uniform vec4 axis_color;
uniform float axis_width;

out vec4 color_vertex;

const float M_PI = 3.1415926;


vec4 get_lightning(vec3 p, vec3 a, vec3 b, mat4 transform)
{
    vec4 v_color = axis_color;
    vec3 norm =  vec3(0,0,0);//normalize();
    vec3 pos = (u_proj_mat*u_view_mat*u_model_mat*transform*vec4(p, 1)).xyz;

    if (u_light_bool[1] == 1){
        float ambientStrength = 0.1;
        vec3 ambient = ambientStrength * u_light_color;
        vec3 lightDir = normalize(u_light_pos - pos);  
        float diff = abs(dot(norm, lightDir));
        vec3 diffuse = diff * u_light_color;

        float specularStrength = 0.5;
        vec3 viewDir = normalize(u_view_pos - pos);
        vec3 reflectDir = reflect(-lightDir, norm);
        float spec = pow(abs(dot(viewDir, reflectDir)), 256);
        vec3 specular = specularStrength * spec * u_light_color;
        
        vec3 result = (ambient + diffuse + specular) * vec3(v_color);
        return vec4(result, v_color[3]);
    } else {
        return v_color;
    }
}

void main()
{
    vec3 positions[2] = vec3[](
        gl_in[0].gl_Position.xyz,
        gl_in[1].gl_Position.xyz
    );

    color_vertex = vec4(1,1,1,1);
}