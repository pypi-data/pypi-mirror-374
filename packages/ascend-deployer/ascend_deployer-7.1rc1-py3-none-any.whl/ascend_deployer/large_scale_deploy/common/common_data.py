from large_scale_deploy.tools.log_tool import LogTool


def _generate_file_handler(file_name):
    return LogTool.get_rotating_file_handler(file_name)


_LARGE_SCALE_LOG_FILE_NAME = "large_scale_deploy.log"
_FILE_HANDLER = LogTool.get_rotating_file_handler(_LARGE_SCALE_LOG_FILE_NAME)
_CONSOLE_HANDLER = LogTool.get_console_handler()

LS_LOGGER = LogTool.generate_logger("LargeScale", [_FILE_HANDLER])
LS_CONSOLE_LOGGER = LogTool.generate_logger("LargeScaleConsole",
                                            [_FILE_HANDLER, _CONSOLE_HANDLER])
