//------------------------------------------------------------------------------
//  triangle-wgpu.c
//  Vertex buffer, simple shader, pipeline state object.
//------------------------------------------------------------------------------
#include "wgpu_entry.h"
#define SOKOL_IMPL
#define SOKOL_WGPU
#include "sokol_gfx.h"
#include "sokol_log.h"

static struct {
    sg_pipeline pip;
    sg_bindings bind;
    sg_pass_action pass_action;
} state = {
    .pass_action = {
        .colors[0] = { .load_action = SG_LOADACTION_CLEAR, .clear_value = { 0.0f, 0.0f, 0.0f, 1.0f } }
    }
};

static void init(void) {
    sg_setup(&(sg_desc){
        .environment = wgpu_environment(),
        .logger.func = slog_func,
    });

    // a vertex buffer with 3 vertices
    float vertices[] = {
        // positions            // colors
         0.0f,  0.5f, 0.5f,     1.0f, 0.0f, 0.0f, 1.0f,
         0.5f, -0.5f, 0.5f,     0.0f, 1.0f, 0.0f, 1.0f,
        -0.5f, -0.5f, 0.5f,     0.0f, 0.0f, 1.0f, 1.0f
    };
    state.bind.vertex_buffers[0] = sg_make_buffer(&(sg_buffer_desc){
        .data = SG_RANGE(vertices)
    });

    // a shader object with wgsl shader code
    sg_shader shd = sg_make_shader(&(sg_shader_desc){
        .vs.source =
            "struct vs_out {\n"
            "  @builtin(position) pos: vec4f,\n"
            "  @location(0) color: vec4f,\n"
            "}\n"
            "@vertex fn main(@location(0) pos: vec4f, @location(1) color: vec4f) -> vs_out {\n"
            "  var out: vs_out;\n"
            "  out.pos = pos;\n"
            "  out.color = color;\n"
            "  return out;\n"
            "}\n",
        .fs.source =
            "@fragment fn main(@location(0) color: vec4f) -> @location(0) vec4f {\n"
            "  return color;\n"
            "}\n",
    });

    // create a pipeline object (default render states are fine for triangle)
    state.pip = sg_make_pipeline(&(sg_pipeline_desc){
        .shader = shd,
        .layout = {
            .attrs = {
                [0].format=SG_VERTEXFORMAT_FLOAT3,
                [1].format=SG_VERTEXFORMAT_FLOAT4
            },
        },
    });
}

static void frame(void) {
    sg_begin_pass(&(sg_pass){ .action = state.pass_action, .swapchain = wgpu_swapchain() });
    sg_apply_pipeline(state.pip);
    sg_apply_bindings(&state.bind);
    sg_draw(0, 3, 1);
    sg_end_pass();
    sg_commit();
}

static void shutdown(void) {
    sg_shutdown();
}

int main() {
    wgpu_start(&(wgpu_desc_t){
        .init_cb = init,
        .frame_cb = frame,
        .shutdown_cb = shutdown,
        .width = 640,
        .height = 480,
        .no_depth_buffer = true,
        .title = "triangle-wgpu"
    });
    return 0;
}
