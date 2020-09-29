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

uniform float grid_thickness;

const float M_PI = 3.1415926;

void main()
{

    // Load the positions
    vec3 positions[] = vec3[](
        (u_view_mat*u_model_mat*gl_in[0].gl_Position).xyz,
        (u_view_mat*u_model_mat*gl_in[1].gl_Position).xyz
    );

    // extract the 90 degree rotation
    vec3 line_vec = normalize(vec3(
        -(positions[1].y-positions[0].y),
        positions[1].x-positions[0].x, 0
    ));

    //Emit the vertices
    gl_Position = u_proj_mat * vec4(positions[0]+grid_thickness*line_vec,1);
    EmitVertex();
    gl_Position = u_proj_mat * vec4(positions[0]-grid_thickness*line_vec,1);
    EmitVertex();
    gl_Position = u_proj_mat * vec4(positions[1]+grid_thickness*line_vec,1);
    EmitVertex();
    gl_Position = u_proj_mat * vec4(positions[1]-grid_thickness*line_vec,1);
    EmitVertex();
    
}