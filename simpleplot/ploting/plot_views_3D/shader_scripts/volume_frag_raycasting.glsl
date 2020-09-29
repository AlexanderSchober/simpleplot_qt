#version 410

out vec4 a_colour;

uniform mat4 u_view_mat;
uniform mat3 u_norm_mat;
uniform mat4 u_model_mat;

uniform float focal_length;
uniform float aspect_ratio;
uniform vec2 viewport_size;
uniform vec3 u_view_pos;
uniform vec3 top;
uniform vec3 bottom;
uniform vec3 background_colour;
uniform vec3 u_light_pos;
uniform float step_length;
uniform float threshold;

uniform vec4 top_limits;
uniform vec4 bot_limits;

uniform float positions[100];
uniform float colors[400];
uniform float min_max[2];
uniform float dimensions[2];

uniform sampler3D volume;


// Ray
struct Ray {
    vec3 origin;
    vec3 direction;
};

// Axis-aligned bounding box
struct AABB {
    vec3 top;
    vec3 bottom;
};

AABB get_bounding_box()
{
    vec4 cube_vectors[8] = vec4[](
        vec4(top.x, top.y, top.z, 1),
        vec4(bottom.x, top.y, top.z, 1),
        vec4(top.x, bottom.y, top.z, 1),
        vec4(bottom.x, bottom.y, top.z, 1),
        vec4(top.x, top.y, bottom.z, 1),
        vec4(bottom.x, top.y, bottom.z, 1),
        vec4(top.x, bottom.y, bottom.z, 1),
        vec4(bottom.x, bottom.y, bottom.z, 1)
    );
    vec4 trans_cube_vectors[8];
    for (int i =0 ; i < 8; ++i){
        trans_cube_vectors[i] = u_model_mat*cube_vectors[i];
    }
    vec3 max_vec = vec3(-1e10,-1e10,-1e10);
    vec3 min_vec = vec3(1e10,1e10,1e10);
    for (int i =0 ; i < 8; ++i){
        max_vec.x = max(max_vec.x, trans_cube_vectors[i].x);
        max_vec.y = max(max_vec.y, trans_cube_vectors[i].y);
        max_vec.z = max(max_vec.z, trans_cube_vectors[i].z);

        min_vec.x = min(min_vec.x, trans_cube_vectors[i].x);
        min_vec.y = min(min_vec.y, trans_cube_vectors[i].y);
        min_vec.z = min(min_vec.z, trans_cube_vectors[i].z);
    }

    return AABB(max_vec, min_vec);
}

// Estimate normal from a finite difference approximation of the gradient
vec3 normal(vec3 position, float intensity)
{
    float d = step_length;
    float dx = texture(volume, position + vec3(d,0,0)).r - intensity;
    float dy = texture(volume, position + vec3(0,d,0)).r - intensity;
    float dz = texture(volume, position + vec3(0,0,d)).r - intensity;
    return -normalize(u_norm_mat * vec3(dx, dy, dz));
}

// Slab method for ray-box intersection
void ray_box_intersection(Ray ray, AABB box, out float t_0, out float t_1)
{
    vec3 direction_inv = 1.0 / ray.direction;
    vec3 t_top = direction_inv * (box.top - ray.origin);
    vec3 t_bottom = direction_inv * (box.bottom - ray.origin);
    vec3 t_min = min(t_top, t_bottom);
    vec2 t = max(t_min.xx, t_min.yz);
    t_0 = max(0.0, max(t.x, t.y));
    vec3 t_max = max(t_top, t_bottom);
    t = min(t_max.xx, t_max.yz);
    t_1 = min(t.x, t.y);
}

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

bool pos_in_box(vec3 position)
{
    if (position.x<bot_limits.x || position.x>top_limits.x)
        return false;
    if (position.y<bot_limits.y || position.y>top_limits.y)
        return false;
    if (position.z<bot_limits.z || position.z>top_limits.z)
        return false;
    return true;
}

void main()
{
    mat4 u_inverse_model_mat = inverse(u_model_mat);

    vec3 ray_direction;
    ray_direction.xy = 2.0 * gl_FragCoord.xy / viewport_size - 1.0;
    ray_direction.x *= aspect_ratio;
    ray_direction.z = -focal_length;
    ray_direction = (vec4(ray_direction, 0)*u_view_mat).xyz;

    float t_0, t_1;
    Ray casting_ray = Ray(u_view_pos, ray_direction);
    AABB bounding_box = get_bounding_box();
    ray_box_intersection(casting_ray, bounding_box, t_0, t_1);

    vec3 ray_start = (u_view_pos + ray_direction * t_0 - bottom) / (top - bottom);
    vec3 ray_stop = (u_view_pos + ray_direction * t_1 - bottom) / (top - bottom);

    vec3 ray = ray_stop - ray_start;
    float ray_length = length(ray);
    vec3 step_vector = step_length * ray / ray_length;

    // Random jitter
    ray_start += step_vector; //* texture(jitter, gl_FragCoord.xy / viewport_size).r;
    vec3 position = ray_start;
    vec4 colorAccum = vec4(0.0);
    
    while (ray_length > 0){
        vec3 texture_pos = (u_inverse_model_mat*vec4(position,1)).xyz;
        if (pos_in_box(texture_pos)){
            float value = texture(volume, texture_pos).r;
            if (value>bot_limits.a && value<top_limits.a){
                vec4 colorSample = colour_transfer(value);
                if (colorSample.a > 0.0) {
                    colorSample.a = 1.0 - pow(1.0 
                    - colorSample.a, step_length*200);
                    colorAccum.rgb += (1.0 - colorAccum.a) * colorSample.rgb * colorSample.a;
                    colorAccum.a += (1.0 - colorAccum.a) * colorSample.a;
                }
            }
        }
        // advance the ray sample position
        ray_length -= step_length;
        position += step_vector;
        
        // if the opacity is (almost) saturated, we can stop raycasting
        if (colorAccum.a > .97) {
            colorAccum.a = 1.0;
            break;
        }
    }
    // blend the background color using an "under" blend operation
    vec4 colour = mix(vec4(background_colour,1), colorAccum, colorAccum.a); 
    a_colour = colour;
}
