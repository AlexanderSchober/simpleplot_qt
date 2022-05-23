#version 400
layout(points) in;
layout(triangle_strip, max_vertices = 120) out;

uniform mat4 u_proj_mat;
uniform mat4 u_view_mat;
uniform mat4 u_model_mat;
uniform vec2 viewport_size;
uniform float line_width = 0.1;
uniform float mode = 5;

in vec4  v_color_frag[];
in float v_radius[];
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
    if (mode==0){
        for (int i = 0; i <= 30; i++) {
            float ang = PI * 2.0 / 30.0;
            vec4 offset ;

            offset = vec4(cos(ang*(i+1)) * (v_radius[0]-line_width)*10/viewport_size[0], -sin(ang*(i+1)) * (v_radius[0]-line_width)*10/viewport_size[1], 0.0, 0.0);
            gl_Position = u_proj_mat*u_view_mat*u_model_mat*(gl_in[0].gl_Position) + offset;
            EmitVertex();

            offset = vec4(cos(ang*(i+1)) * (v_radius[0]+line_width)*10/viewport_size[0], -sin(ang*(i+1)) * (v_radius[0]+line_width)*10/viewport_size[1], 0.0, 0.0);
            gl_Position = u_proj_mat*u_view_mat*u_model_mat*(gl_in[0].gl_Position) + offset;
            EmitVertex();

            offset = vec4(cos(ang*i) * (v_radius[0]-line_width)*10/viewport_size[0], -sin(ang*i) * (v_radius[0]-line_width)*10/viewport_size[1], 0.0, 0.0);
            gl_Position = u_proj_mat*u_view_mat*u_model_mat*(gl_in[0].gl_Position) + offset;
            EmitVertex();

            offset = vec4(cos(ang*i) * (v_radius[0]+line_width)*10/viewport_size[0], -sin(ang*i) * (v_radius[0]+line_width)*10/viewport_size[1], 0.0, 0.0);
            gl_Position = u_proj_mat*u_view_mat*u_model_mat*(gl_in[0].gl_Position) + offset;
            EmitVertex();

            EndPrimitive();
        }
    } else if (mode==1){
        for (int i = 0; i <= 3; i++) {
            float ang = PI * 2.0 / 3.;
            vec4 offset ;

            offset = vec4(cos(ang*(i+1)+PI / 2.) * (v_radius[0]-line_width)*10/viewport_size[0], -sin(ang*(i+1)+PI / 2.) * (v_radius[0]-line_width)*10/viewport_size[1], 0.0, 0.0);
            gl_Position = u_proj_mat*u_view_mat*u_model_mat*(gl_in[0].gl_Position) + offset;
            EmitVertex();

            offset = vec4(cos(ang*(i+1)+PI / 2.) * (v_radius[0]+line_width)*10/viewport_size[0], -sin(ang*(i+1)+PI / 2.) * (v_radius[0]+line_width)*10/viewport_size[1], 0.0, 0.0);
            gl_Position = u_proj_mat*u_view_mat*u_model_mat*(gl_in[0].gl_Position) + offset;
            EmitVertex();

            offset = vec4(cos(ang*i+PI / 2.) * (v_radius[0]-line_width)*10/viewport_size[0], -sin(ang*i+PI / 2.) * (v_radius[0]-line_width)*10/viewport_size[1], 0.0, 0.0);
            gl_Position = u_proj_mat*u_view_mat*u_model_mat*(gl_in[0].gl_Position) + offset;
            EmitVertex();

            offset = vec4(cos(ang*i+PI / 2.) * (v_radius[0]+line_width)*10/viewport_size[0], -sin(ang*i+PI / 2.) * (v_radius[0]+line_width)*10/viewport_size[1], 0.0, 0.0);
            gl_Position = u_proj_mat*u_view_mat*u_model_mat*(gl_in[0].gl_Position) + offset;
            EmitVertex();

            EndPrimitive();
        }
    } else if (mode==2){
        for (int i = 0; i <= 3; i++) {
            float ang = PI * 2.0 / 3.;
            vec4 offset ;

            offset = vec4(cos(ang*(i+1)-PI / 2.) * (v_radius[0]-line_width)*10/viewport_size[0], -sin(ang*(i+1)-PI / 2.) * (v_radius[0]-line_width)*10/viewport_size[1], 0.0, 0.0);
            gl_Position = u_proj_mat*u_view_mat*u_model_mat*(gl_in[0].gl_Position) + offset;
            EmitVertex();

            offset = vec4(cos(ang*(i+1)-PI / 2.) * (v_radius[0]+line_width)*10/viewport_size[0], -sin(ang*(i+1)-PI / 2.) * (v_radius[0]+line_width)*10/viewport_size[1], 0.0, 0.0);
            gl_Position = u_proj_mat*u_view_mat*u_model_mat*(gl_in[0].gl_Position) + offset;
            EmitVertex();

            offset = vec4(cos(ang*i-PI / 2.) * (v_radius[0]-line_width)*10/viewport_size[0], -sin(ang*i-PI / 2.) * (v_radius[0]-line_width)*10/viewport_size[1], 0.0, 0.0);
            gl_Position = u_proj_mat*u_view_mat*u_model_mat*(gl_in[0].gl_Position) + offset;
            EmitVertex();

            offset = vec4(cos(ang*i-PI / 2.) * (v_radius[0]+line_width)*10/viewport_size[0], -sin(ang*i-PI / 2.) * (v_radius[0]+line_width)*10/viewport_size[1], 0.0, 0.0);
            gl_Position = u_proj_mat*u_view_mat*u_model_mat*(gl_in[0].gl_Position) + offset;
            EmitVertex();

            EndPrimitive();
        }
    } else if (mode==3){
        for (int i = 0; i <= 3; i++) {
            float ang = PI * 2.0 / 3.;
            vec4 offset ;

            offset = vec4(cos(ang*(i+1)) * (v_radius[0]-line_width)*10/viewport_size[0], -sin(ang*(i+1)) * (v_radius[0]-line_width)*10/viewport_size[1], 0.0, 0.0);
            gl_Position = u_proj_mat*u_view_mat*u_model_mat*(gl_in[0].gl_Position) + offset;
            EmitVertex();

            offset = vec4(cos(ang*(i+1)) * (v_radius[0]+line_width)*10/viewport_size[0], -sin(ang*(i+1)) * (v_radius[0]+line_width)*10/viewport_size[1], 0.0, 0.0);
            gl_Position = u_proj_mat*u_view_mat*u_model_mat*(gl_in[0].gl_Position) + offset;
            EmitVertex();

            offset = vec4(cos(ang*i) * (v_radius[0]-line_width)*10/viewport_size[0], -sin(ang*i) * (v_radius[0]-line_width)*10/viewport_size[1], 0.0, 0.0);
            gl_Position = u_proj_mat*u_view_mat*u_model_mat*(gl_in[0].gl_Position) + offset;
            EmitVertex();

            offset = vec4(cos(ang*i) * (v_radius[0]+line_width)*10/viewport_size[0], -sin(ang*i) * (v_radius[0]+line_width)*10/viewport_size[1], 0.0, 0.0);
            gl_Position = u_proj_mat*u_view_mat*u_model_mat*(gl_in[0].gl_Position) + offset;
            EmitVertex();

            EndPrimitive();
        }
    } else if (mode==4){
        for (int i = 0; i <= 3; i++) {
            float ang = PI * 2.0 / 3.;
            vec4 offset ;

            offset = vec4(cos(ang*(i+1)+PI) * (v_radius[0]-line_width)*10/viewport_size[0], -sin(ang*(i+1)+PI) * (v_radius[0]-line_width)*10/viewport_size[1], 0.0, 0.0);
            gl_Position = u_proj_mat*u_view_mat*u_model_mat*(gl_in[0].gl_Position) + offset;
            EmitVertex();

            offset = vec4(cos(ang*(i+1)+PI) * (v_radius[0]+line_width)*10/viewport_size[0], -sin(ang*(i+1)+PI) * (v_radius[0]+line_width)*10/viewport_size[1], 0.0, 0.0);
            gl_Position = u_proj_mat*u_view_mat*u_model_mat*(gl_in[0].gl_Position) + offset;
            EmitVertex();

            offset = vec4(cos(ang*i+PI) * (v_radius[0]-line_width)*10/viewport_size[0], -sin(ang*i+PI) * (v_radius[0]-line_width)*10/viewport_size[1], 0.0, 0.0);
            gl_Position = u_proj_mat*u_view_mat*u_model_mat*(gl_in[0].gl_Position) + offset;
            EmitVertex();

            offset = vec4(cos(ang*i+PI) * (v_radius[0]+line_width)*10/viewport_size[0], -sin(ang*i+PI) * (v_radius[0]+line_width)*10/viewport_size[1], 0.0, 0.0);
            gl_Position = u_proj_mat*u_view_mat*u_model_mat*(gl_in[0].gl_Position) + offset;
            EmitVertex();

            EndPrimitive();
        }
    } else if (mode==5){
        for (int i = 0; i <= 4; i++) {
            float ang = PI * 2.0 / 4.;
            vec4 offset ;

            offset = vec4(cos(ang*(i+1)-PI / 2.) * (v_radius[0]-line_width)*10/viewport_size[0], -sin(ang*(i+1)-PI / 2.) * (v_radius[0]-line_width)*10/viewport_size[1], 0.0, 0.0);
            gl_Position = u_proj_mat*u_view_mat*u_model_mat*(gl_in[0].gl_Position) + offset;
            EmitVertex();

            offset = vec4(cos(ang*(i+1)-PI / 2.) * (v_radius[0]+line_width)*10/viewport_size[0], -sin(ang*(i+1)-PI / 2.) * (v_radius[0]+line_width)*10/viewport_size[1], 0.0, 0.0);
            gl_Position = u_proj_mat*u_view_mat*u_model_mat*(gl_in[0].gl_Position) + offset;
            EmitVertex();

            offset = vec4(cos(ang*i-PI / 2.) * (v_radius[0]-line_width)*10/viewport_size[0], -sin(ang*i-PI / 2.) * (v_radius[0]-line_width)*10/viewport_size[1], 0.0, 0.0);
            gl_Position = u_proj_mat*u_view_mat*u_model_mat*(gl_in[0].gl_Position) + offset;
            EmitVertex();

            offset = vec4(cos(ang*i-PI / 2.) * (v_radius[0]+line_width)*10/viewport_size[0], -sin(ang*i-PI / 2.) * (v_radius[0]+line_width)*10/viewport_size[1], 0.0, 0.0);
            gl_Position = u_proj_mat*u_view_mat*u_model_mat*(gl_in[0].gl_Position) + offset;
            EmitVertex();

            EndPrimitive();
        }
    } else if (mode==6){
        for (int i = 0; i <= 4; i++) {
            float ang = PI * 2.0 / 4.;
            vec4 offset ;

            offset = vec4(cos(ang*(i+1)-PI / 4.) * (v_radius[0]-line_width)*10/viewport_size[0], -sin(ang*(i+1)-PI / 4.) * (v_radius[0]-line_width)*10/viewport_size[1], 0.0, 0.0);
            gl_Position = u_proj_mat*u_view_mat*u_model_mat*(gl_in[0].gl_Position) + offset;
            EmitVertex();

            offset = vec4(cos(ang*(i+1)-PI / 4.) * (v_radius[0]+line_width)*10/viewport_size[0], -sin(ang*(i+1)-PI / 4.) * (v_radius[0]+line_width)*10/viewport_size[1], 0.0, 0.0);
            gl_Position = u_proj_mat*u_view_mat*u_model_mat*(gl_in[0].gl_Position) + offset;
            EmitVertex();

            offset = vec4(cos(ang*i-PI / 4.) * (v_radius[0]-line_width)*10/viewport_size[0], -sin(ang*i-PI / 4.) * (v_radius[0]-line_width)*10/viewport_size[1], 0.0, 0.0);
            gl_Position = u_proj_mat*u_view_mat*u_model_mat*(gl_in[0].gl_Position) + offset;
            EmitVertex();

            offset = vec4(cos(ang*i-PI / 4.) * (v_radius[0]+line_width)*10/viewport_size[0], -sin(ang*i-PI / 4.) * (v_radius[0]+line_width)*10/viewport_size[1], 0.0, 0.0);
            gl_Position = u_proj_mat*u_view_mat*u_model_mat*(gl_in[0].gl_Position) + offset;
            EmitVertex();

            EndPrimitive();
        }
    } else if (mode==7){
        for (int i = 0; i <= 5; i++) {
            float ang = PI * 2.0 / 5.;
            vec4 offset ;

            offset = vec4(cos(ang*(i+1)) * (v_radius[0]-line_width)*10/viewport_size[0], -sin(ang*(i+1)) * (v_radius[0]-line_width)*10/viewport_size[1], 0.0, 0.0);
            gl_Position = u_proj_mat*u_view_mat*u_model_mat*(gl_in[0].gl_Position) + offset;
            EmitVertex();

            offset = vec4(cos(ang*(i+1)) * (v_radius[0]+line_width)*10/viewport_size[0], -sin(ang*(i+1)) * (v_radius[0]+line_width)*10/viewport_size[1], 0.0, 0.0);
            gl_Position = u_proj_mat*u_view_mat*u_model_mat*(gl_in[0].gl_Position) + offset;
            EmitVertex();

            offset = vec4(cos(ang*i) * (v_radius[0]-line_width)*10/viewport_size[0], -sin(ang*i) * (v_radius[0]-line_width)*10/viewport_size[1], 0.0, 0.0);
            gl_Position = u_proj_mat*u_view_mat*u_model_mat*(gl_in[0].gl_Position) + offset;
            EmitVertex();

            offset = vec4(cos(ang*i) * (v_radius[0]+line_width)*10/viewport_size[0], -sin(ang*i) * (v_radius[0]+line_width)*10/viewport_size[1], 0.0, 0.0);
            gl_Position = u_proj_mat*u_view_mat*u_model_mat*(gl_in[0].gl_Position) + offset;
            EmitVertex();

            EndPrimitive();
        }
    } else if (mode==8){
        for (int i = 0; i <= 6; i++) {
            float ang = PI * 2.0 / 6.;
            vec4 offset ;

            offset = vec4(cos(ang*(i+1)) * (v_radius[0]-line_width)*10/viewport_size[0], -sin(ang*(i+1)) * (v_radius[0]-line_width)*10/viewport_size[1], 0.0, 0.0);
            gl_Position = u_proj_mat*u_view_mat*u_model_mat*(gl_in[0].gl_Position) + offset;
            EmitVertex();

            offset = vec4(cos(ang*(i+1)) * (v_radius[0]+line_width)*10/viewport_size[0], -sin(ang*(i+1)) * (v_radius[0]+line_width)*10/viewport_size[1], 0.0, 0.0);
            gl_Position = u_proj_mat*u_view_mat*u_model_mat*(gl_in[0].gl_Position) + offset;
            EmitVertex();

            offset = vec4(cos(ang*i) * (v_radius[0]-line_width)*10/viewport_size[0], -sin(ang*i) * (v_radius[0]-line_width)*10/viewport_size[1], 0.0, 0.0);
            gl_Position = u_proj_mat*u_view_mat*u_model_mat*(gl_in[0].gl_Position) + offset;
            EmitVertex();

            offset = vec4(cos(ang*i) * (v_radius[0]+line_width)*10/viewport_size[0], -sin(ang*i) * (v_radius[0]+line_width)*10/viewport_size[1], 0.0, 0.0);
            gl_Position = u_proj_mat*u_view_mat*u_model_mat*(gl_in[0].gl_Position) + offset;
            EmitVertex();

            EndPrimitive();
        }
    } else if (mode==9){

        vec4 offset[26]  = vec4[](
            vec4(-(v_radius[0]/3.-line_width)*10/(viewport_size[0]),  (v_radius[0]   -line_width)*10/(viewport_size[1]), 0.0, 0.0),
            vec4(-(v_radius[0]/3.+line_width)*10/(viewport_size[0]),  (v_radius[0]   +line_width)*10/(viewport_size[1]), 0.0, 0.0),
            vec4( (v_radius[0]/3.-line_width)*10/(viewport_size[0]),  (v_radius[0]   -line_width)*10/(viewport_size[1]), 0.0, 0.0),
            vec4( (v_radius[0]/3.+line_width)*10/(viewport_size[0]),  (v_radius[0]   +line_width)*10/(viewport_size[1]), 0.0, 0.0),
            vec4( (v_radius[0]/3.-line_width)*10/(viewport_size[0]),  (v_radius[0]/3.-line_width)*10/(viewport_size[1]), 0.0, 0.0),
            vec4( (v_radius[0]/3.+line_width)*10/(viewport_size[0]),  (v_radius[0]/3.+line_width)*10/(viewport_size[1]), 0.0, 0.0),
            vec4( (v_radius[0]   -line_width)*10/(viewport_size[0]),  (v_radius[0]/3.-line_width)*10/(viewport_size[1]), 0.0, 0.0),
            vec4( (v_radius[0]   +line_width)*10/(viewport_size[0]),  (v_radius[0]/3.+line_width)*10/(viewport_size[1]), 0.0, 0.0),
            vec4( (v_radius[0]   -line_width)*10/(viewport_size[0]), -(v_radius[0]/3.-line_width)*10/(viewport_size[1]), 0.0, 0.0),
            vec4( (v_radius[0]   +line_width)*10/(viewport_size[0]), -(v_radius[0]/3.+line_width)*10/(viewport_size[1]), 0.0, 0.0),
            vec4( (v_radius[0]/3.-line_width)*10/(viewport_size[0]), -(v_radius[0]/3.-line_width)*10/(viewport_size[1]), 0.0, 0.0),
            vec4( (v_radius[0]/3.+line_width)*10/(viewport_size[0]), -(v_radius[0]/3.+line_width)*10/(viewport_size[1]), 0.0, 0.0),
            vec4( (v_radius[0]/3.-line_width)*10/(viewport_size[0]), -(v_radius[0]   -line_width)*10/(viewport_size[1]), 0.0, 0.0),
            vec4( (v_radius[0]/3.+line_width)*10/(viewport_size[0]), -(v_radius[0]   +line_width)*10/(viewport_size[1]), 0.0, 0.0),
            vec4(-(v_radius[0]/3.-line_width)*10/(viewport_size[0]), -(v_radius[0]   -line_width)*10/(viewport_size[1]), 0.0, 0.0),
            vec4(-(v_radius[0]/3.+line_width)*10/(viewport_size[0]), -(v_radius[0]   +line_width)*10/(viewport_size[1]), 0.0, 0.0),
            vec4(-(v_radius[0]/3.-line_width)*10/(viewport_size[0]), -(v_radius[0]/3.-line_width)*10/(viewport_size[1]), 0.0, 0.0),
            vec4(-(v_radius[0]/3.+line_width)*10/(viewport_size[0]), -(v_radius[0]/3.+line_width)*10/(viewport_size[1]), 0.0, 0.0),
            vec4(-(v_radius[0]   -line_width)*10/(viewport_size[0]), -(v_radius[0]/3.-line_width)*10/(viewport_size[1]), 0.0, 0.0),
            vec4(-(v_radius[0]   +line_width)*10/(viewport_size[0]), -(v_radius[0]/3.+line_width)*10/(viewport_size[1]), 0.0, 0.0),
            vec4(-(v_radius[0]   -line_width)*10/(viewport_size[0]),  (v_radius[0]/3.-line_width)*10/(viewport_size[1]), 0.0, 0.0),
            vec4(-(v_radius[0]   +line_width)*10/(viewport_size[0]),  (v_radius[0]/3.+line_width)*10/(viewport_size[1]), 0.0, 0.0),
            vec4(-(v_radius[0]/3.-line_width)*10/(viewport_size[0]),  (v_radius[0]/3.-line_width)*10/(viewport_size[1]), 0.0, 0.0),
            vec4(-(v_radius[0]/3.+line_width)*10/(viewport_size[0]),  (v_radius[0]/3.+line_width)*10/(viewport_size[1]), 0.0, 0.0),
            vec4(-(v_radius[0]/3.-line_width)*10/(viewport_size[0]),  (v_radius[0]   -line_width)*10/(viewport_size[1]), 0.0, 0.0),
            vec4(-(v_radius[0]/3.+line_width)*10/(viewport_size[0]),  (v_radius[0]   +line_width)*10/(viewport_size[1]), 0.0, 0.0)
        );

        for(int i = 0; i < 26; ++i){
            gl_Position = u_proj_mat*u_view_mat*u_model_mat*(gl_in[0].gl_Position) + offset[i];
            EmitVertex();
        }
        EndPrimitive();

    } else if (mode==10){

        vec4 offset[26]  = vec4[](
            vec4(-(v_radius[0]/3.-line_width)*10/(viewport_size[0]),  (v_radius[0]   -line_width)*10/(viewport_size[1]), 0.0, 0.0),
            vec4(-(v_radius[0]/3.+line_width)*10/(viewport_size[0]),  (v_radius[0]   +line_width)*10/(viewport_size[1]), 0.0, 0.0),
            vec4( (v_radius[0]/3.-line_width)*10/(viewport_size[0]),  (v_radius[0]   -line_width)*10/(viewport_size[1]), 0.0, 0.0),
            vec4( (v_radius[0]/3.+line_width)*10/(viewport_size[0]),  (v_radius[0]   +line_width)*10/(viewport_size[1]), 0.0, 0.0),
            vec4( (v_radius[0]/3.-line_width)*10/(viewport_size[0]),  (v_radius[0]/3.-line_width)*10/(viewport_size[1]), 0.0, 0.0),
            vec4( (v_radius[0]/3.+line_width)*10/(viewport_size[0]),  (v_radius[0]/3.+line_width)*10/(viewport_size[1]), 0.0, 0.0),
            vec4( (v_radius[0]   -line_width)*10/(viewport_size[0]),  (v_radius[0]/3.-line_width)*10/(viewport_size[1]), 0.0, 0.0),
            vec4( (v_radius[0]   +line_width)*10/(viewport_size[0]),  (v_radius[0]/3.+line_width)*10/(viewport_size[1]), 0.0, 0.0),
            vec4( (v_radius[0]   -line_width)*10/(viewport_size[0]), -(v_radius[0]/3.-line_width)*10/(viewport_size[1]), 0.0, 0.0),
            vec4( (v_radius[0]   +line_width)*10/(viewport_size[0]), -(v_radius[0]/3.+line_width)*10/(viewport_size[1]), 0.0, 0.0),
            vec4( (v_radius[0]/3.-line_width)*10/(viewport_size[0]), -(v_radius[0]/3.-line_width)*10/(viewport_size[1]), 0.0, 0.0),
            vec4( (v_radius[0]/3.+line_width)*10/(viewport_size[0]), -(v_radius[0]/3.+line_width)*10/(viewport_size[1]), 0.0, 0.0),
            vec4( (v_radius[0]/3.-line_width)*10/(viewport_size[0]), -(v_radius[0]   -line_width)*10/(viewport_size[1]), 0.0, 0.0),
            vec4( (v_radius[0]/3.+line_width)*10/(viewport_size[0]), -(v_radius[0]   +line_width)*10/(viewport_size[1]), 0.0, 0.0),
            vec4(-(v_radius[0]/3.-line_width)*10/(viewport_size[0]), -(v_radius[0]   -line_width)*10/(viewport_size[1]), 0.0, 0.0),
            vec4(-(v_radius[0]/3.+line_width)*10/(viewport_size[0]), -(v_radius[0]   +line_width)*10/(viewport_size[1]), 0.0, 0.0),
            vec4(-(v_radius[0]/3.-line_width)*10/(viewport_size[0]), -(v_radius[0]/3.-line_width)*10/(viewport_size[1]), 0.0, 0.0),
            vec4(-(v_radius[0]/3.+line_width)*10/(viewport_size[0]), -(v_radius[0]/3.+line_width)*10/(viewport_size[1]), 0.0, 0.0),
            vec4(-(v_radius[0]   -line_width)*10/(viewport_size[0]), -(v_radius[0]/3.-line_width)*10/(viewport_size[1]), 0.0, 0.0),
            vec4(-(v_radius[0]   +line_width)*10/(viewport_size[0]), -(v_radius[0]/3.+line_width)*10/(viewport_size[1]), 0.0, 0.0),
            vec4(-(v_radius[0]   -line_width)*10/(viewport_size[0]),  (v_radius[0]/3.-line_width)*10/(viewport_size[1]), 0.0, 0.0),
            vec4(-(v_radius[0]   +line_width)*10/(viewport_size[0]),  (v_radius[0]/3.+line_width)*10/(viewport_size[1]), 0.0, 0.0),
            vec4(-(v_radius[0]/3.-line_width)*10/(viewport_size[0]),  (v_radius[0]/3.-line_width)*10/(viewport_size[1]), 0.0, 0.0),
            vec4(-(v_radius[0]/3.+line_width)*10/(viewport_size[0]),  (v_radius[0]/3.+line_width)*10/(viewport_size[1]), 0.0, 0.0),
            vec4(-(v_radius[0]/3.-line_width)*10/(viewport_size[0]),  (v_radius[0]   -line_width)*10/(viewport_size[1]), 0.0, 0.0),
            vec4(-(v_radius[0]/3.+line_width)*10/(viewport_size[0]),  (v_radius[0]   +line_width)*10/(viewport_size[1]), 0.0, 0.0)
        );

        for(int i = 0; i < 26; ++i){
            gl_Position = vec4(
                rotatePoint((u_proj_mat*u_view_mat*u_model_mat*(gl_in[0].gl_Position) + offset[i]).xy, (u_proj_mat*u_view_mat*u_model_mat*(gl_in[0].gl_Position)).xy, 45.),
                (u_proj_mat*u_view_mat*u_model_mat*(gl_in[0].gl_Position)).z, 1) ;
            EmitVertex();
        }
        EndPrimitive();

    }
    
}