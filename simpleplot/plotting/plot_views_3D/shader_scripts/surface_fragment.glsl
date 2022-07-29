#version 400

in vec3 v_normal;
in vec4 v_color;

in float light_active;
in vec3 light_pos;
in vec3 view_pos;
in vec3 frag_pos;
in vec3 light_color;

uniform float positions[100];
uniform float colors[400];
uniform float min_max[2];
uniform float dimensions[2];

// A very simple colour transfer function
vec4 colour_transfer(float z_value)
{
    vec4 color;
    float z_norm = (z_value - min_max[0]) / (min_max[1] - min_max[0]);
    for (int i = 0; i < dimensions[0]; i++){
        if (z_norm >= positions[i] && z_norm <= positions[i+1] ){
            float z_local = (z_norm-positions[i])/(positions[i+1]-positions[i]);
            for (int j = 0; j < dimensions[1]; j++){
                color[j] =  colors[i*4+j] + (colors[(i+1)*4+j]-colors[i*4+j])*z_local;
            }
        }
    }
    return color;
}

out vec4 f_color;
void main() {
    vec4 v_color = colour_transfer(frag_pos[2]);
    if (light_active == 1){
        float ambientStrength = 0.1;
        vec3 ambient = ambientStrength * light_color;
        vec3 norm = normalize(v_normal);
        vec3 lightDir = normalize(light_pos - frag_pos);  
        float diff = max(dot(norm, lightDir), 0.0);
        vec3 diffuse = diff * light_color;

        float specularStrength = 0.5;
        vec3 viewDir = normalize(view_pos - frag_pos);
        vec3 reflectDir = reflect(-lightDir, norm);
        float spec = pow(max(dot(viewDir, reflectDir), 0.0), 256);
        vec3 specular = specularStrength * spec * light_color;
        
        vec3 result = (ambient + diffuse + specular) * vec3(v_color);
        f_color = vec4(result, v_color[3]);
    } else {
        f_color = v_color;
    }
}
