#include <stdio.h>
#include <string.h>
#include <lua.h>
#include <lauxlib.h>
#include <lualib.h>

/* https://www.lua.org/pil/24.1.html */

int instructions = 0;

void instr_count (lua_State *L, lua_Debug *D) {
    instructions += 1;
}

int main (int argc, char *argv[]) {
    char buff[256];
    int error;
    lua_State *L = luaL_newstate();   /* opens Lua */
    luaL_openlibs(L);            /* opens the Lua libraries. */

    lua_sethook(L, *instr_count, LUA_MASKCOUNT, 1);

    error = luaL_dofile(L, argv[1]);
    if (error) {
        fprintf(stderr, "E:%s\n", lua_tostring(L, -1));
        lua_pop(L, 1);  /* pop error message from the stack */
    }

    printf("Instruction count: %d\n", instructions);

    lua_close(L);
    return 0;
}