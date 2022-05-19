#version 400
layout(points) in;
layout(triangle_strip, max_vertices = 90) out;

uniform mat4 u_proj_mat;
uniform mat4 u_view_mat;
uniform mat4 u_model_mat;

in vec4  v_color_frag[];
in float v_radius[];
out vec4  f_color;

const float PI = 3.1415926;

void main()
{
    f_color = v_color_frag[0];
    for (int i = 0; i <= 30; i++) {
        float ang = PI * 2.0 / 30.0;
        vec4 offset ;

        gl_Position = u_proj_mat*u_view_mat*u_model_mat*(gl_in[0].gl_Position);
        EmitVertex();

        offset = vec4(cos(ang*(i+1)) * v_radius[0], -sin(ang*(i+1)) * v_radius[0], 0.0, 0.0);
        gl_Position = u_proj_mat*u_view_mat*u_model_mat*(gl_in[0].gl_Position) + offset;
        EmitVertex();

        offset = vec4(cos(ang*i) * v_radius[0], -sin(ang*i) * v_radius[0], 0.0, 0.0);
        gl_Position = u_proj_mat*u_view_mat*u_model_mat*(gl_in[0].gl_Position) + offset;
        EmitVertex();

        EndPrimitive();
    }

}