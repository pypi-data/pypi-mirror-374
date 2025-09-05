#include "vpi_user.h"

typedef void (voidfn)(void);

extern voidfn <%-startupCall%>;

voidfn * vlog_startup_routines[] = {
    <%-startupCall%>,
    0
};

