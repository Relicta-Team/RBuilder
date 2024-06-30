
//возвращает корневую директорию сервера
ReBridge_getWorkspace = {
	call compile (engineCall(getworkspace) select 0)
};