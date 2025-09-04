import logging
import logging.handlers
import os
import stat
import sys

CUR_DIR = os.path.dirname(os.path.realpath(__file__))


class LogTool:

    @classmethod
    def get_log_dir(cls):
        if 'site-packages' not in CUR_DIR and 'dist-packages' not in CUR_DIR:
            log_dir = os.path.dirname(CUR_DIR)
        else:
            if os.getenv('ASCEND_DEPLOYER_HOME'):
                deployer_home = os.getenv('ASCEND_DEPLOYER_HOME')
            else:
                deployer_home = os.getcwd()
            log_dir = os.path.join(deployer_home, "ascend-deployer")
        return log_dir

    @classmethod
    def get_log_format(cls):
        format_string = \
            "%(asctime)s downloader [%(levelname)s] " \
            "[%(filename)s:%(lineno)d %(funcName)s] %(message)s"
        date_format = '%Y-%m-%d %H:%M:%S'
        return logging.Formatter(format_string, date_format)

    @classmethod
    def chmod_log_file(cls, file_path):
        if not os.path.exists(file_path):
            os.close(os.open(file_path, os.O_CREAT, stat.S_IRUSR | stat.S_IWUSR))
        else:
            os.chmod(file_path, stat.S_IRUSR | stat.S_IWUSR)

    @classmethod
    def get_rotating_conf(cls):
        return dict(mode='a',
                    maxBytes=20 * 1024 * 1024,
                    backupCount=5,
                    encoding="UTF-8"
                    )

    @classmethod
    def get_log_level(cls):
        return os.environ.get("ASCEND_DEPLOYER_LOG_LEVEL", logging.INFO)

    @classmethod
    def get_rotating_file_handler(cls, file_name: str):
        log_dir = LogTool.get_log_dir()
        file_path = os.path.join(log_dir, file_name)
        handler = logging.handlers.RotatingFileHandler(filename=file_path, **LogTool.get_rotating_conf())
        handler.setFormatter(cls.get_log_format())
        return handler

    @classmethod
    def get_console_handler(cls):
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(cls.get_log_format())
        return console_handler

    @classmethod
    def generate_logger(cls, logger_name, handlers):
        logger = logging.getLogger(logger_name)
        logger.setLevel(cls.get_log_level())
        for handler in handlers:
            logger.addHandler(handler)
        return logger
