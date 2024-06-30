
/*
    calculates expression in compile time
    _num = constexpr {3+5};

    constexpr variable = 435;

    constexpr function = {
        variable + 5
    }


*/
#define constexpr LANG_CONSTEXPR;

/*
    static assert expression in compile time
    static_assert(call function + 1 == 441);
*/
#define static_assert(expr) EVAL_EXPR_RET expr

//special compiler flag
#define pragma

//function or variable returns constant value - cannot be changed
//func/meth param cannot be changed inside
/*
    const testFunc = {
        params [const "_arg1","_arg2"];
    };

    const testvariable = 1;

    const func(test)
    {
        objParams_2(const _a,const _b)
    };

*/
#define const LANG_CONST+

//function or variable can be get value via reflection
//member name no applied optimization/renaming 
/*
    reflect rttfunc = {};
    noreflectfunc = {};
    missionnamespace getvariable ["rtt"+"func"];//ok
    missionanamespace getvariable ["noreflectfunc"];//error
*/
#define reflect

//force inline function, method, constvariable value
#define inline LANG_INLINE;

//next code block will be inlined without any optimization and changes
/*
    _b = native {
        _a = 1+2;
        _a
    }
*/
#define native LANG_NATIVE;

/*
    mark local variable as getting from upper scope without passing param
    fnc = {
        stackvar _a;
        _b = _a;
    };
    _a = 5;
    call fnc;
*/
#define stackvar 

// special mark for methods - method called from type (do not accessed with object)
#define const_func

// get file,line,function before vm preprocessing
#define __PFILE__
#define __PLINE__
#define __PFUNC__