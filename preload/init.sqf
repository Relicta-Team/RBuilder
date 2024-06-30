// ======================================================
// Copyright (c) 2017-2024 the ReSDK_A3 project
// sdk.relicta.ru
// ======================================================

/*
    Main RBuilder loader.
    RBuilder can used for:
        - unit tests
        - parsing code
        - compiling, executing code
*/

#include <..\host\engine.hpp>


isRBuilder = true;

//RBuilder_password - use as serverpassword
server_password = RBuilder_password;

diag_log ("[RB] Initialize cba module");
call compile preprocessFileLineNumbers "preload\rbuilder_cba_functions.sqf";

diag_log ("[RB] Loading cba initializer");
call compile preprocessFileLineNumbers "preload\rbuilder_cba_init.sqf";

//called after logger functions loaded
RBuilder_postInit = {

    rbPrint = {
        params ["_msg",["_fncaller","Unknown_function"]];
        "debug_console" CALLEXTENSION (format["RBuilder(%2): %1",_msg,_fncaller]);
    };

    #define __strval__(v__) 'v__'
    #define definePrinter(__name) \
    __name = { \
        private _ftData = _this; \
        if equalTypes(_ftData,[]) then { \
            if (count _ftData > 0 && {equalTypes(_ftData select 0,"")}) then { \
                _ftData = format _ftData; \
            }; \
        }; \
        [_ftData, __strval__(__name) ] call rbPrint; \
    };

    definePrinter(cprint)
    definePrinter(cprintErr)
    definePrinter(cprintWarn)
    definePrinter(discLog)
    definePrinter(discError)
    definePrinter(discWarning)


    definePrinter(logCritical)
    definePrinter(logError)
    definePrinter(logWarn)
    definePrinter(logInfo)
    definePrinter(logDebug)
    definePrinter(logTrace)

    definePrinter(systemLog)
    definePrinter(gameLog)
    definePrinter(rpLog)
    definePrinter(lifeLog)
    definePrinter(adminLog)
    definePrinter(combatLog)


};
call RBuilder_postInit; //preinit logfile



//initialize rebgidge
["STAGE INITIALIZE REBRIDGE"] call cprint;

#include "..\src\ReBridge\ReBridge_init.sqf"

//load rebridge_getWorkspace
#include "_not_implemented.sqf"

// активируем компонет
[] call ReBridge_start;
// Загрузим проект со скриптами (Путь должен быть полным)

private _scriptPath = ((call ReBridge_getWorkspace) + ("\Scripts\RBuilder.reproj"));
["Script ReBridge path: %1",_scriptPath] call cprint;

private _buildResult = [_scriptPath] call rescript_build;
if (_buildResult != "ok") exitWith {
    ["ReBridge initialization error; Result: %1",_buildResult] call cprintErr;
    call rbuilder_fatalShutdownServer;
};

["Initialize scripts..."] call cprint;

["Breakpoint"] call rescript_initScript;
["ScriptContext"] call rescript_initScript;
["WorkspaceHelper"] call rescript_initScript;
["FileManager"] call rescript_initScript;
["RBuilder"] call rescript_initScript;

//todo remove this test critical exit
["RBuilder","exit",[-100500]] call rescript_callCommandVoid;


//always needed. outside this check nullval
true