// Linux stand-in for vk_menu.cpp (the Insert menu): the options at their documented defaults and a menu
// that is never open, so the rest of the back end links unchanged. The real menu reads Win32 keyboard
// state (GetAsyncKeyState, GetForegroundWindow); wiring it here needs host-side key plumbing first.
#include "vk_menu.h"

namespace mkwvk {

Options opts;   // (out of the box every feature is off)

void menu_init() {}
void menu_tick() {}
bool menu_is_open() { return false; }
void menu_note_frame(bool game_frame) { (void)game_frame; }
void menu_record(VkCommandBuffer cmd, VkImage dst, int slot, uint32_t w, uint32_t h) {
    (void)cmd; (void)dst; (void)slot; (void)w; (void)h;
}

}  // namespace mkwvk
