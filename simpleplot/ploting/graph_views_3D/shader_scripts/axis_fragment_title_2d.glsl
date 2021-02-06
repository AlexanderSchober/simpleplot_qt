#version 410

//in vec4 texture_coordinate;
out vec4 fragment_color;
uniform vec4 title_color = vec4(0,1,0,1);
uniform sampler2D text_texture;
uniform vec2 viewport_size;
uniform vec4 title_parameters;

void main() {
    vec2 fragment_position = 2.0 * gl_FragCoord.xy / viewport_size - 1.0;
    vec2 relative_position = vec2(
        (fragment_position.x - (title_parameters.x - title_parameters.b / 2)) / title_parameters.b,
        (fragment_position.y - (title_parameters.y - title_parameters.a / 2)) / title_parameters.a
    );
    fragment_color = vec4(
        title_color.rgb,
        texture(text_texture, vec2(relative_position.x, 1-relative_position.y)).r
        * title_color.a
    );
}

