#version 330

layout (location = 0) in vec3 a_position;
layout (location = 1) in vec3 a_color;


uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

uniform mat4 translation;
uniform mat4 scale;

out vec3 v_color;

void main()
{
    gl_Position = projection * view * model * translation * scale * vec4(a_position, 1.0);
    v_color = a_color;
}
