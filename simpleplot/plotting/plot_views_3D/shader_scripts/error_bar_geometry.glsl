#version 400
layout(points) in;
layout(triangle_strip, max_vertices = 120) out;

uniform mat4 u_proj_mat;
uniform mat4 u_view_mat;
uniform mat4 u_model_mat;

uniform vec2 viewport_size;
uniform float line_width = 0.1;
uniform float beam_width = 0.5;
uniform float mode = 0;

in vec4  v_color_frag[];
in vec2  x_error_frag[];
in vec2  y_error_frag[];
// in vec2  z_error_frag[];

out vec4  f_color;

const float PI = 3.1415926;

vec2 rotatePoint(vec2 point_in, vec2 center, float angle){
    vec2 point_out;
    float rotation_angle = (angle / 180) * 3.145;
    mat2 roation_mat = mat2(cos(rotation_angle), sin(rotation_angle), - sin(rotation_angle), cos(rotation_angle));
    vec2 center_px = (center+1)/2 * viewport_size;
    vec2 point_in_px = (point_in+1)/2 * viewport_size;
    point_out = roation_mat * (point_in_px - center_px) + center_px;
    return (point_out / viewport_size)*2 - 1;
}

void main()
{
    f_color = v_color_frag[0];
    vec4 pos;
    vec4 offset;
    vec4 center = u_proj_mat*u_view_mat*u_model_mat*(gl_in[0].gl_Position);

    //left error bar
    if (x_error_frag[0].x != 0) {
        pos = u_proj_mat*u_view_mat*u_model_mat*vec4(gl_in[0].gl_Position.x - x_error_frag[0].x, gl_in[0].gl_Position.yzw);

        offset = vec4(-(line_width*10/viewport_size[0]),  (beam_width*10/viewport_size[1]), 0.0, 0.0);
        gl_Position = pos + offset;
        EmitVertex();

        offset = vec4( (line_width*10/viewport_size[0]),  (beam_width*10/viewport_size[1]), 0.0, 0.0);
        gl_Position = pos + offset;
        EmitVertex();

        offset = vec4(-(line_width*10/viewport_size[0]), -(beam_width*10/viewport_size[1]), 0.0, 0.0);
        gl_Position = pos + offset;
        EmitVertex();

        offset = vec4( (line_width*10/viewport_size[0]), -(beam_width*10/viewport_size[0]), 0.0, 0.0);
        gl_Position = pos + offset;
        EmitVertex();
        EndPrimitive();

        offset = vec4(0, -(line_width*10/viewport_size[1]), 0.0, 0.0);
        gl_Position = pos + offset;
        EmitVertex();

        offset = vec4(0,  (line_width*10/viewport_size[1]), 0.0, 0.0);
        gl_Position = pos + offset;
        EmitVertex();

        offset = vec4(0, -(line_width*10/viewport_size[1]), 0.0, 0.0);
        gl_Position = center + offset;
        EmitVertex();

        offset = vec4(0,  (line_width*10/viewport_size[1]), 0.0, 0.0);
        gl_Position = center + offset;
        EmitVertex();
        EndPrimitive();
    }

    //Right error bar
    if (x_error_frag[0].y != 0) {
        pos = u_proj_mat*u_view_mat*u_model_mat*vec4(gl_in[0].gl_Position.x + x_error_frag[0].y, gl_in[0].gl_Position.yzw);

        offset = vec4(-(line_width*10/viewport_size[0]),  (beam_width*10/viewport_size[1]), 0.0, 0.0);
        gl_Position = pos + offset;
        EmitVertex();

        offset = vec4( (line_width*10/viewport_size[0]),  (beam_width*10/viewport_size[1]), 0.0, 0.0);
        gl_Position = pos + offset;
        EmitVertex();

        offset = vec4(-(line_width*10/viewport_size[0]), -(beam_width*10/viewport_size[1]), 0.0, 0.0);
        gl_Position = pos + offset;
        EmitVertex();

        offset = vec4( (line_width*10/viewport_size[0]), -(beam_width*10/viewport_size[1]), 0.0, 0.0);
        gl_Position = pos + offset;
        EmitVertex();
        EndPrimitive();

        offset = vec4(0, -(line_width*10/viewport_size[1]), 0.0, 0.0);
        gl_Position = center + offset;
        EmitVertex();

        offset = vec4(0,  (line_width*10/viewport_size[1]), 0.0, 0.0);
        gl_Position = center + offset;
        EmitVertex();

        offset = vec4(0, -(line_width*10/viewport_size[1]), 0.0, 0.0);
        gl_Position = pos + offset;
        EmitVertex();

        offset = vec4(0,  (line_width*10/viewport_size[1]), 0.0, 0.0);
        gl_Position = pos + offset;
        EmitVertex();
        EndPrimitive();
    }

    //top error bar
    if (y_error_frag[0].x != 0) {
        pos = u_proj_mat*u_view_mat*u_model_mat*vec4(gl_in[0].gl_Position.x, gl_in[0].gl_Position.y + y_error_frag[0].x, gl_in[0].gl_Position.zw);

        offset = vec4(-(beam_width*10/viewport_size[0]),  (line_width*10/viewport_size[1]), 0.0, 0.0);
        gl_Position = pos + offset;
        EmitVertex();

        offset = vec4( (beam_width*10/viewport_size[0]),  (line_width*10/viewport_size[1]), 0.0, 0.0);
        gl_Position = pos + offset;
        EmitVertex();

        offset = vec4(-(beam_width*10/viewport_size[0]), -(line_width*10/viewport_size[1]), 0.0, 0.0);
        gl_Position = pos + offset;
        EmitVertex();

        offset = vec4( (beam_width*10/viewport_size[0]), -(line_width*10/viewport_size[1]), 0.0, 0.0);
        gl_Position = pos + offset;
        EmitVertex();
        EndPrimitive();

        offset = vec4(-(line_width*10/viewport_size[0]), 0.0, 0.0, 0.0);
        gl_Position = pos + offset;
        EmitVertex();

        offset = vec4((line_width*10/viewport_size[0]), 0., 0.0, 0.0);
        gl_Position = pos + offset;
        EmitVertex();

        offset = vec4(-(line_width*10/viewport_size[0]), 0.0, 0.0, 0.0);
        gl_Position = center + offset;
        EmitVertex();

        offset = vec4((line_width*10/viewport_size[0]), 0., 0.0, 0.0);
        gl_Position = center + offset;
        EmitVertex();
        EndPrimitive();
    }

    //bot error bar
    if (y_error_frag[0].y != 0) {
        pos = u_proj_mat*u_view_mat*u_model_mat*vec4(gl_in[0].gl_Position.x, gl_in[0].gl_Position.y - y_error_frag[0].y, gl_in[0].gl_Position.zw);

        offset = vec4(-(beam_width*10/viewport_size[0]),  (line_width*10/viewport_size[1]), 0.0, 0.0);
        gl_Position = pos + offset;
        EmitVertex();

        offset = vec4( (beam_width*10/viewport_size[0]),  (line_width*10/viewport_size[1]), 0.0, 0.0);
        gl_Position = pos + offset;
        EmitVertex();

        offset = vec4(-(beam_width*10/viewport_size[0]), -(line_width*10/viewport_size[1]), 0.0, 0.0);
        gl_Position = pos + offset;
        EmitVertex();

        offset = vec4( (beam_width*10/viewport_size[0]), -(line_width*10/viewport_size[1]), 0.0, 0.0);
        gl_Position = pos + offset;
        EmitVertex();
        EndPrimitive();

        offset = vec4(-(line_width*10/viewport_size[0]), 0.0, 0.0, 0.0);
        gl_Position = center + offset;
        EmitVertex();

        offset = vec4((line_width*10/viewport_size[0]), 0., 0.0, 0.0);
        gl_Position = center + offset;
        EmitVertex();

        offset = vec4(-(line_width*10/viewport_size[0]), 0.0, 0.0, 0.0);
        gl_Position = pos + offset;
        EmitVertex();

        offset = vec4((line_width*10/viewport_size[0]), 0., 0.0, 0.0);
        gl_Position = pos + offset;
        EmitVertex();
        EndPrimitive();
    }

}