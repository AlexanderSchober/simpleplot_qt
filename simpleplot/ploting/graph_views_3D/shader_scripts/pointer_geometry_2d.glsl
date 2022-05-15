#version 410
layout(points) in;
layout(triangle_strip, max_vertices = 60) out;

uniform float z_near = -1.;
uniform vec2 viewport_size;
uniform float pointer_thickness = 1.;
uniform float pointer_size= 1;

void main()
{
    vec4 position = gl_in[0].gl_Position;
    
    vec2 viewport_pixel_size = 2. / viewport_size;

    //top
    gl_Position = vec4(vec2(-pointer_thickness/2., pointer_thickness/2) * viewport_pixel_size, 0., 1.) + vec4(position.xy, z_near, 0);
    EmitVertex();

    gl_Position = vec4(vec2(-pointer_thickness/2., pointer_size) * viewport_pixel_size, 0., 1.) + vec4(position.xy, z_near, 0);
    EmitVertex();

    gl_Position = vec4(vec2( pointer_thickness/2., pointer_thickness/2.) * viewport_pixel_size, 0., 1.) + vec4(position.xy, z_near, 0);
    EmitVertex();

    gl_Position = vec4(vec2( pointer_thickness/2., pointer_size) * viewport_pixel_size, 0., 1.) + vec4(position.xy, z_near, 0);
    EmitVertex();

    EndPrimitive();

    // //right
    gl_Position = vec4(vec2( pointer_thickness/2., pointer_thickness/2.) * viewport_pixel_size, 0., 1.) + vec4(position.xy, z_near, 0);
    EmitVertex();

    gl_Position = vec4(vec2( pointer_size, pointer_thickness/2.) * viewport_pixel_size, 0., 1.) + vec4(position.xy, z_near, 0);
    EmitVertex();

    gl_Position = vec4(vec2( pointer_thickness/2., -pointer_thickness/2.) * viewport_pixel_size, 0., 1.) + vec4(position.xy, z_near, 0);
    EmitVertex();

    gl_Position = vec4(vec2( pointer_size, -pointer_thickness/2.) * viewport_pixel_size, 0., 1.) + vec4(position.xy, z_near, 0);
    EmitVertex();

    EndPrimitive();

    //bot
    gl_Position = vec4(vec2( pointer_thickness/2., -pointer_thickness/2.) * viewport_pixel_size, 0., 1.) + vec4(position.xy, z_near, 0);
    EmitVertex();

    gl_Position = vec4(vec2( pointer_thickness/2., -pointer_size) * viewport_pixel_size, 0., 1.) + vec4(position.xy, z_near, 0);
    EmitVertex();

    gl_Position = vec4(vec2(-pointer_thickness/2., -pointer_thickness/2.) * viewport_pixel_size, 0., 1.) + vec4(position.xy, z_near, 0);
    EmitVertex();

    gl_Position = vec4(vec2(-pointer_thickness/2., -pointer_size) * viewport_pixel_size, 0., 1.) + vec4(position.xy, z_near, 0);
    EmitVertex();

    EndPrimitive();

    //left

    gl_Position = vec4(vec2(-pointer_thickness/2., -pointer_thickness/2.) * viewport_pixel_size, 0., 1.) + vec4(position.xy, z_near, 0);
    EmitVertex();

    gl_Position = vec4(vec2(-pointer_size, -pointer_thickness/2.) * viewport_pixel_size, 0., 1.) + vec4(position.xy, z_near, 0);
    EmitVertex();

    gl_Position = vec4(vec2(-pointer_thickness/2.,  pointer_thickness/2.) * viewport_pixel_size, 0., 1.) + vec4(position.xy, z_near, 0);
    EmitVertex();

    gl_Position = vec4(vec2(-pointer_size, pointer_thickness/2.) * viewport_pixel_size, 0., 1.) + vec4(position.xy, z_near, 0);
    EmitVertex();

    EndPrimitive();

}