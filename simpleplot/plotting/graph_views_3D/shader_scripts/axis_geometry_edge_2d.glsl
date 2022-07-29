#version 410
layout(triangles) in;
layout(triangle_strip, max_vertices = 3) out;

uniform mat4 u_proj_mat;
uniform mat4 u_view_mat;
uniform mat4 u_model_mat;

uniform float z_near = -0.990;

out vec4 color_vertex;

void main()
{
    // get the pointsi
    vec3 positions[3] = vec3[](
        gl_in[0].gl_Position.xyz,
        gl_in[1].gl_Position.xyz,
        gl_in[2].gl_Position.xyz
    );

    gl_Position = vec4((positions[0]).xy, z_near, 1);
    EmitVertex();
    gl_Position = vec4((positions[1]).xy, z_near, 1);
    EmitVertex();
    gl_Position = vec4((positions[2]).xy, z_near, 1);
    EmitVertex();
    EndPrimitive();
}