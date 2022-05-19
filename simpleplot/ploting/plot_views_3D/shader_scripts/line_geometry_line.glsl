#version 410
layout(triangles) in;
layout(triangle_strip, max_vertices = 34) out;

uniform mat4 u_proj_mat;
uniform mat4 u_view_mat;
uniform mat4 u_model_mat;

uniform vec3 u_view_pos;
uniform vec2 u_light_bool;
uniform vec3 u_light_pos;
uniform vec3 u_light_color;

uniform vec4 line_color;
uniform float line_width;

out vec4 color_vertex;

const float M_PI = 3.1415926;

vec3 position_on_line(vec3 p, vec3 a, vec3 b)
{
    vec3 ap = p-a;
    vec3 ab = b-a; 
    return a+(dot(ap,ab)/dot(ab,ab))*ab;
}

vec4 get_lightning(vec3 p, vec3 a, vec3 b, mat4 transform)
{
    vec4 v_color = line_color;
    vec3 norm =  normalize((u_proj_mat*u_view_mat*u_model_mat*transform*vec4(p - position_on_line(p, a, b),0)).xyz);
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
    vec3 positions[3] = vec3[](
        (u_proj_mat*u_view_mat*u_model_mat*gl_in[0].gl_Position).xyz,
        (u_proj_mat*u_view_mat*u_model_mat*gl_in[1].gl_Position).xyz,
        (u_proj_mat*u_view_mat*u_model_mat*gl_in[2].gl_Position).xyz
    );

    //******************************************************************************
    // First process the main compound
    vec3 direction      = positions[1]-positions[0];
    float direction_len = length(direction);
    float gamma         = -asin(clamp(direction.z/direction_len,-1,1));
    if(acos(direction.x/sqrt(direction.x*direction.x+direction.y*direction.y)) >= M_PI/2){
        if (gamma<0){
            gamma = M_PI + gamma;
        } else {
            gamma = -M_PI - gamma;
        }
    } 

    float theta = acos(clamp(direction.x/(direction_len*cos(gamma)),-1,1)); 
    if(asin(direction.y/(direction_len*cos(gamma))) < 0){
        theta = - theta;
    } 
    
    mat4 transform = mat4(
        cos(theta)*cos(gamma), sin(theta) * cos(gamma), -sin(gamma), 0,
        -sin(theta), cos(theta), 0, 0,
        cos(theta) * sin(gamma), sin(theta) * sin(gamma), cos(gamma), 0,
        positions[0].x, positions[0].y, positions[0].z, 0
    );

    vec4 outputs[14] = vec4[](
        vec4(0,line_width,line_width,1),
        vec4(direction_len,line_width,line_width,1),
        vec4(0,-line_width,line_width,1),
        vec4(direction_len,-line_width,line_width,1),
        vec4(direction_len,-line_width,-line_width,1),
        vec4(direction_len,line_width,line_width,1),
        vec4(direction_len,line_width,-line_width,1),
        vec4(0,line_width,line_width,1),
        vec4(0,line_width,-line_width,1),
        vec4(0,-line_width,line_width,1),
        vec4(0,-line_width,-line_width,1),
        vec4(direction_len,-line_width,-line_width,1),
        vec4(0,line_width,-line_width,1),
        vec4(direction_len,line_width,-line_width,1)
    ); 
    for(int i = 0; i < 14;++i ){
        color_vertex = get_lightning(outputs[i].xyz, positions[0], positions[1], transform);
        gl_Position = vec4((transform*outputs[i]).xyz,1);
        EmitVertex();
    }
    EndPrimitive();

    //******************************************************************************
    // Second process the junction compound
    vec3 direction_j      = positions[2]-positions[1];
    float direction_j_len = length(direction_j);
    float gamma_j         = -asin(direction_j.z/direction_j_len);
    if(acos(sqrt(direction_j.x*direction_j.x+direction_j.y*direction_j.y)/direction_j_len) > M_PI/2){
        if (gamma_j<0){
            gamma_j = M_PI + gamma_j;
        } else {
            gamma_j = M_PI - gamma_j;
        }
    } 

    float theta_j = acos(direction_j.x/(direction_j_len*cos(gamma_j))); 
    if(asin(direction_j.y/(direction_j_len*cos(gamma_j))) < 0){
        theta_j = - theta_j;
    } 
    
    // get the both tranform matrices for the vector
    mat4 transform_j_0 = mat4(
        cos(theta)*cos(gamma), sin(theta) * cos(gamma), -sin(gamma), 0,
        -sin(theta), cos(theta), 0, 0,
        cos(theta) * sin(gamma), sin(theta) * sin(gamma), cos(gamma), 0,
        positions[0].x, positions[0].y, positions[0].z, 0
    );

    mat4 transform_j_1 = mat4(
        cos(theta_j)*cos(gamma_j), sin(theta_j) * cos(gamma_j), -sin(gamma_j), 0,
        -sin(theta_j), cos(theta_j), 0, 0,
        cos(theta_j) * sin(gamma_j), sin(theta_j) * sin(gamma_j), cos(gamma_j),0,
        positions[1].x, positions[1].y, positions[1].z, 0
    );

    vec4 frame[8] = vec4[](
        transform_j_0*vec4(direction_len,-line_width,-line_width,1),
        transform_j_0*vec4(direction_len,-line_width,line_width,1),
        transform_j_0*vec4(direction_len,line_width,line_width,1),
        transform_j_0*vec4(direction_len,line_width,-line_width,1),

        transform_j_1*vec4(0,-line_width,-line_width,1),
        transform_j_1*vec4(0,-line_width,line_width,1),
        transform_j_1*vec4(0,line_width,line_width,1),
        transform_j_1*vec4(0,line_width,-line_width,1)
    );

    int indices[20] = int[](1,5,0,4,1,2,6,1,5,2,3,7,2,6,3,0,4,3,7,0);

    for(int j = 0; j < 20;++j){
        color_vertex = get_lightning(frame[indices[j]].xyz, positions[0], positions[2], transform);
        gl_Position = vec4(frame[indices[j]].xyz,1);
        EmitVertex();
    }

    EndPrimitive();


}