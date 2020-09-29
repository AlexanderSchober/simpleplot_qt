#version 410
layout(lines) in;
layout(triangle_strip, max_vertices = 4) out;

uniform mat4 u_proj_mat;
uniform mat4 u_view_mat;
uniform mat4 u_model_mat;

uniform vec3 u_view_pos;
uniform vec2 u_light_bool;
uniform vec3 u_light_pos;
uniform vec3 u_light_color;

uniform vec4 fill_color;
uniform float fill_level;
uniform vec3 fill_axis_start;
uniform vec3 fill_axis_end;

out vec4 color_vertex;

vec3 position_on_line(vec3 a, vec3 b, vec3 p)
{
    vec3 ap = p-a;
    vec3 ab = b-a; 
    return a+dot(ap,ab)/dot(ab,ab)*ab;
}

vec4 get_lightning(vec4 a, vec4 b, vec4 c)
{
    vec4 v_color = fill_color;
    vec3 norm = cross((b-a).xyz, (c-a).xyz);
    norm = normalize(norm);

    if (u_light_bool[1] == 1){
        float ambientStrength = 0.1;
        vec3 ambient = ambientStrength * u_light_color;
        vec3 lightDir = normalize(u_light_pos - a.xyz);  
        float diff = max(abs(dot(norm, lightDir)), 0.0);
        vec3 diffuse = diff * u_light_color;

        float specularStrength = 0.5;
        vec3 viewDir = normalize(u_view_pos - a.xyz);
        vec3 reflectDir = reflect(-lightDir, norm);
        float spec = pow(max(abs(dot(viewDir, reflectDir)), 0.0), 256);
        vec3 specular = specularStrength * spec * u_light_color;
        
        vec3 result = (ambient + diffuse + specular) * vec3(v_color);
        return vec4(result, v_color[3]);
    } else {
        return v_color;
    }
}

void main()
{
    vec3 t_fill_axis_start = (u_view_mat*u_model_mat*vec4(fill_axis_start,1)).xyz;
    vec3 t_fill_axis_end = (u_view_mat*u_model_mat*vec4(fill_axis_end,1)).xyz;
    vec4 positions[4] = vec4[](
        u_proj_mat*u_view_mat*u_model_mat*gl_in[0].gl_Position,
        u_proj_mat*u_view_mat*u_model_mat*gl_in[1].gl_Position,
        u_proj_mat*vec4(position_on_line(
            t_fill_axis_start, 
            t_fill_axis_end, 
            (u_view_mat*u_model_mat*gl_in[0].gl_Position).xyz),1),
        u_proj_mat*vec4(position_on_line(
            t_fill_axis_start, 
            t_fill_axis_end, 
            (u_view_mat*u_model_mat*gl_in[1].gl_Position).xyz),1)
    );

    gl_Position = positions[2];
    color_vertex = get_lightning(positions[2], positions[3], positions[0]);
    EmitVertex();
    gl_Position = positions[0];
    color_vertex = get_lightning(positions[0], positions[2], positions[3]);
    EmitVertex();
    gl_Position = positions[3];
    color_vertex = get_lightning(positions[3], positions[1], positions[2]);
    EmitVertex();
    gl_Position = positions[1];
    color_vertex = get_lightning(positions[1], positions[0], positions[3]);
    EmitVertex();
}