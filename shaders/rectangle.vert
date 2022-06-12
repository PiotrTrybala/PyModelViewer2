#version 330

layout (location = 0) in vec3 a_position;
layout (location = 1) in vec3 a_color;

out vec3 v_color;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

void main()
{
    gl_Position = projection * view * model * vec4(a_position, 1.0);
    v_color = vec3(1.0, 0.5, 0.0);
}
