#version 410
layout(lines) in;
layout(triangle_strip, max_vertices = 120) out;

uniform mat4 u_proj_mat;
uniform mat4 u_view_mat;
uniform mat4 u_model_mat;

uniform float near_plane;
uniform float aspect_ratio;
uniform vec2 viewport_size;
uniform vec2 position_offset;

uniform vec3 u_view_pos;
uniform vec2 u_light_bool;
uniform vec3 u_light_pos;
uniform vec3 u_light_color;
uniform vec3 u_center_pos;

uniform vec2 axis_length;
uniform vec3 axis_direction;
uniform vec3 axis_center;
uniform vec4 axis_color;
uniform float axis_width;

uniform float axis_arrow_width;
uniform float axis_arrow_length;
uniform float axis_scale_factor;

out vec4 color_vertex;

const float M_PI = 3.1415926;

// Get the lightning color depending on the orientation
vec4 get_lightning(vec3 pos, vec3 direction)
{
    vec4 v_color = axis_color;
    vec3 norm = normalize(direction);

    if (u_light_bool[0] == 1){
        float ambientStrength = 0.1;
        vec3 ambient    = ambientStrength * u_light_color;
        vec3 lightDir   = normalize(u_light_pos - pos);  
        float diff      = max(dot(norm, lightDir),0);
        vec3 diffuse    = diff * u_light_color;

        float specularStrength = 0.5;
        vec3 viewDir        = normalize(u_view_pos - pos);
        vec3 reflectDir     = reflect(-lightDir, norm);
        float spec          = pow(max(dot(viewDir, reflectDir),0), 256);
        vec3 specular       = specularStrength * spec * u_light_color;
        
        vec3 result = (ambient + diffuse + specular) * vec3(v_color);
        return vec4(result, v_color[3]);
    } else {
        return v_color;
    }
}

// Get the tranform to project one vector onto the other
mat4 get_transform(vec3 from_vector, vec3 to_vector)
{
    vec3 norm_from_vector = normalize(from_vector);// 1,0,0
    vec3 norm_to_vector = normalize(to_vector);//0,0,1

    vec3 axis = cross( norm_from_vector, norm_to_vector );//0,1,0
    float cosA = dot( norm_from_vector, norm_to_vector );//0
    float k = 1.0f / (1.0f + cosA);//1

    vec3 pos = normalize(u_center_pos - u_view_pos);

    mat4 result = mat4( 
        (axis.x * axis.x * k) + cosA,       //0
        (axis.x * axis.y * k) + axis.z,     //0
        (axis.x * axis.z * k) - axis.y,     //1
        0,                                  //0

        (axis.y * axis.x * k) - axis.z,     //0
        (axis.y * axis.y * k) + cosA,       //1
        (axis.y * axis.z * k) + axis.x,     //0
        0,                                  //0

        (axis.z * axis.x * k) + axis.y,     //1
        (axis.z * axis.y * k) - axis.x,     //0
        (axis.z * axis.z * k) + cosA,       //0
        0,                                  //0
        
        u_view_pos[0] + pos[0]*axis_scale_factor,
        u_view_pos[1] + pos[1]*axis_scale_factor,
        u_view_pos[2] + pos[2]*axis_scale_factor,
        1
    );

    //  0  0  1   1     0 
    //  0  1  0   0     0
    //  1  0  0   0     1

    return result;
}

void main()
{
    // get the points
    vec3 positions[2] = vec3[](
        gl_in[0].gl_Position.xyz,
        gl_in[1].gl_Position.xyz
    );

    vec3 offset_vec3;
    offset_vec3.xy = 2*position_offset/ viewport_size - 1.0;
    offset_vec3.z = -near_plane;
    vec4 offset = vec4(offset_vec3,0);

    // Get the transform
    mat4 transform = get_transform(vec3(1,0,0), axis_direction);
    mat4 total_transform = transform;

    // Set up the start and end circles
    vec4 start_circle[10];
    vec4 end_circle[10];
    vec4 arrow_circle[10];
    for (int i = 0 ; i < 10 ; ++i ){
        start_circle[i] = total_transform * vec4(
            axis_length[0], axis_width*cos(2*M_PI/10*i), axis_width*sin(2*M_PI/10*i),1);
        end_circle[i] = total_transform * vec4(
            axis_length[1], axis_width*cos(2*M_PI/10*i), axis_width*sin(2*M_PI/10*i),1);
        arrow_circle[i] = total_transform * vec4(
            axis_length[1], axis_arrow_width*cos(2*M_PI/10*i), axis_arrow_width*sin(2*M_PI/10*i),1);
    }

    // Get the end points
    vec4 start_point    = total_transform * vec4(axis_length[0],0,0,1);
    vec4 start_vec      = total_transform * vec4(axis_length[0],0,0,0);
    vec4 start_color    = get_lightning(start_point.xyz, start_vec.xyz);

    vec4 end_point      = total_transform * vec4(axis_length[1]+axis_arrow_length,0,0,1);
    vec4 end_vec        = total_transform * vec4(axis_length[1]+axis_arrow_length,0,0,0);
    vec4 end_color      = get_lightning(end_point.xyz, end_vec.xyz);

    // ---------------------------------------------------------------------
    // Set the front fans
    for (int i = 0 ; i < 9 ; ++i ){
        color_vertex = start_color;
        gl_Position = u_proj_mat*u_view_mat*u_model_mat*start_point;
gl_Position.xy += offset.xy*gl_Position.w;
        gl_Position.z = gl_Position.z/100;
        EmitVertex();
        
        color_vertex = get_lightning(start_circle[i].xyz, start_vec.xyz);
        gl_Position = u_proj_mat*u_view_mat*u_model_mat*start_circle[i];
gl_Position.xy += offset.xy*gl_Position.w;
        gl_Position.z = gl_Position.z/100;
        EmitVertex();

        color_vertex = get_lightning(start_circle[i+1].xyz, start_vec.xyz);
        gl_Position = u_proj_mat*u_view_mat*u_model_mat*start_circle[i+1];
gl_Position.xy += offset.xy*gl_Position.w;
        gl_Position.z = gl_Position.z/100;
        EmitVertex();

        EndPrimitive();
    }

    color_vertex = start_color;
    gl_Position = u_proj_mat*u_view_mat*u_model_mat*start_point;
gl_Position.xy += offset.xy*gl_Position.w;
    gl_Position.z = gl_Position.z/100;
    EmitVertex();
    
    color_vertex = get_lightning(start_circle[9].xyz, start_vec.xyz);
    gl_Position = u_proj_mat*u_view_mat*u_model_mat*start_circle[9];
gl_Position.xy += offset.xy*gl_Position.w;
    gl_Position.z = gl_Position.z/100;
    EmitVertex();

    color_vertex = get_lightning(start_circle[0].xyz, start_vec.xyz);
    gl_Position = u_proj_mat*u_view_mat*u_model_mat*start_circle[0];
gl_Position.xy += offset.xy*gl_Position.w;
    gl_Position.z = gl_Position.z/100;
    EmitVertex();

    EndPrimitive();

    // ---------------------------------------------------------------------
    // Set the tube fans
    for (int i = 0 ; i < 10 ; ++i ){
        color_vertex = get_lightning(start_circle[i].xyz, start_circle[i].xyz - start_point.xyz);
        gl_Position = u_proj_mat*u_view_mat*u_model_mat*  start_circle[i];
gl_Position.xy += offset.xy*gl_Position.w;
        gl_Position.z = gl_Position.z/100;
    EmitVertex();

        color_vertex = get_lightning(end_circle[i].xyz, end_circle[i].xyz - end_point.xyz);
        gl_Position = u_proj_mat*u_view_mat*u_model_mat*end_circle[i];
gl_Position.xy += offset.xy*gl_Position.w;
        gl_Position.z = gl_Position.z/100;
    EmitVertex();
    }

    color_vertex = get_lightning(start_circle[0].xyz, start_circle[0].xyz - start_point.xyz);
    gl_Position = u_proj_mat*u_view_mat*u_model_mat* start_circle[0];
gl_Position.xy += offset.xy*gl_Position.w;
    gl_Position.z = gl_Position.z/100;
    EmitVertex();

    color_vertex = get_lightning(end_circle[0].xyz, end_circle[0].xyz - end_point.xyz);
    gl_Position = u_proj_mat*u_view_mat*u_model_mat*end_circle[0];
gl_Position.xy += offset.xy*gl_Position.w;
    gl_Position.z = gl_Position.z/100;
    EmitVertex();
    
    EndPrimitive();

    // ---------------------------------------------------------------------
    // Set the tube connector
    for (int i = 0 ; i < 10 ; ++i ){
        color_vertex = get_lightning(arrow_circle[i].xyz, start_vec.xyz);
        gl_Position = u_proj_mat*u_view_mat*u_model_mat*  arrow_circle[i];
gl_Position.xy += offset.xy*gl_Position.w;
        gl_Position.z = gl_Position.z/100;
    EmitVertex();

        color_vertex = get_lightning(end_circle[i].xyz, start_vec.xyz);
        gl_Position = u_proj_mat*u_view_mat*u_model_mat*end_circle[i];
gl_Position.xy += offset.xy*gl_Position.w;
        gl_Position.z = gl_Position.z/100;
    EmitVertex();
    }

    color_vertex = get_lightning(arrow_circle[0].xyz, start_vec.xyz);
    gl_Position = u_proj_mat*u_view_mat*u_model_mat* arrow_circle[0];
gl_Position.xy += offset.xy*gl_Position.w;
    gl_Position.z = gl_Position.z/100;
    EmitVertex();

    color_vertex = get_lightning(end_circle[0].xyz, start_vec.xyz);
    gl_Position = u_proj_mat*u_view_mat*u_model_mat*end_circle[0];
gl_Position.xy += offset.xy*gl_Position.w;
    gl_Position.z = gl_Position.z/100;
    EmitVertex();
    
    EndPrimitive();

    // ---------------------------------------------------------------------
    // Set the arrow crown fans
    for (int i = 0 ; i < 9 ; ++i ){
        color_vertex = end_color;
        gl_Position = u_proj_mat*u_view_mat*u_model_mat*end_point;
gl_Position.xy += offset.xy*gl_Position.w;
        gl_Position.z = gl_Position.z/100;
    EmitVertex();

        color_vertex = get_lightning(arrow_circle[i].xyz, end_vec.xyz);
        gl_Position = u_proj_mat*u_view_mat*u_model_mat*arrow_circle[i];
gl_Position.xy += offset.xy*gl_Position.w;
        gl_Position.z = gl_Position.z/100;
    EmitVertex();

        color_vertex = get_lightning(arrow_circle[i+1].xyz, end_vec.xyz);
        gl_Position = u_proj_mat*u_view_mat*u_model_mat*arrow_circle[i+1];
gl_Position.xy += offset.xy*gl_Position.w;
        gl_Position.z = gl_Position.z/100;
    EmitVertex();
        
        EndPrimitive();
    }

    color_vertex = end_color;
    gl_Position = u_proj_mat*u_view_mat*u_model_mat*end_point;
gl_Position.xy += offset.xy*gl_Position.w;
    gl_Position.z = gl_Position.z/100;
    EmitVertex();

    color_vertex = get_lightning(arrow_circle[9].xyz, end_vec.xyz);
    gl_Position = u_proj_mat*u_view_mat*u_model_mat*end_circle[9];
gl_Position.xy += offset.xy*gl_Position.w;
    gl_Position.z = gl_Position.z/100;
    EmitVertex();

    color_vertex = get_lightning(arrow_circle[0].xyz, end_vec.xyz);
    gl_Position = u_proj_mat*u_view_mat*u_model_mat*arrow_circle[0];
gl_Position.xy += offset.xy*gl_Position.w;
    gl_Position.z = gl_Position.z/100;
    EmitVertex();
    
    EndPrimitive();
}