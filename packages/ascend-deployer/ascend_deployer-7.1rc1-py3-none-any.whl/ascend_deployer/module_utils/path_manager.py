import os.path
import shutil

_CUR_DIR = os.path.dirname(__file__)


class ProjectPath:
    USER_HOME = os.path.expanduser("~")
    ROOT = os.path.dirname(_CUR_DIR)
    PLAYBOOK_DIR = os.path.join(ROOT, "playbooks")
    INVENTORY_FILE = "inventory_file"
    PROCESS_PLAYBOOK_DIR = os.path.join(PLAYBOOK_DIR, "process")


class TmpPath:
    ROOT = os.path.join(ProjectPath.USER_HOME, ".ascend_deployer")
    DEPLOY_INFO = os.path.join(ROOT, "deploy_info")
    DL_YAML_DIR = os.path.join(ROOT, "dl_yaml")
    PROGRESS_JSON_NAME = "deployer_progress_output.json"
    PROGRESS_JSON = os.path.join(DEPLOY_INFO, PROGRESS_JSON_NAME)
    TEST_REPORT_JSON = os.path.join(DEPLOY_INFO, "test_report.json")
    CHECK_RES_OUTPUT_JSON = os.path.join(DEPLOY_INFO, "check_res_output.json")


class LargeScalePath:
    ROOT_TMP_DIR = os.path.join(TmpPath.ROOT, "large_scale_deploy")
    INVENTORY_FILE_PATH = os.path.join(ProjectPath.ROOT, "large_scale_inventory.ini")
    PARSED_INVENTORY_FILE_PATH = os.path.join(ROOT_TMP_DIR, "parsed_inventory_file.ini")
    DEPLOY_NODE_INVENTORY_FILE_PATH = os.path.join(ROOT_TMP_DIR, "deploy_node_inventory_file.ini")
    REMOTE_DEPLOYER_DIR = os.path.join(ROOT_TMP_DIR, "ascend_deployer")
    REMOTE_INVENTORY_FILE = os.path.join(REMOTE_DEPLOYER_DIR, ProjectPath.INVENTORY_FILE)
    REMOTE_START_SCRIPT = os.path.join(REMOTE_DEPLOYER_DIR, "install.sh")
    REMOTE_EXECUTE_RES_LOG = os.path.join(ROOT_TMP_DIR, "ascend_deployer_execute.log")
    REMOTE_HOST_RESULTS = os.path.join(ROOT_TMP_DIR, "remote_host_data")
    SPREAD_TASK = os.path.join(ROOT_TMP_DIR, "spread_task")
    SPREAD_NODES_TREE_JSON = os.path.join(SPREAD_TASK, "spread_nodes_tree.json")
    EXEC_RESULTS_DIR = os.path.join(SPREAD_TASK, "exec_results")
    REPORT_DIR = os.path.join(ROOT_TMP_DIR, "report")
    ALL_TEST_REPORT_CSV = os.path.join(REPORT_DIR, "test_report.csv")


class PathManager:

    @classmethod
    def recover_dir(cls, dir_path):
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path)
        os.makedirs(dir_path, exist_ok=True)

    @classmethod
    def init_large_scale_dirs(cls):
        cls.recover_dir(LargeScalePath.REMOTE_HOST_RESULTS)
        cls.recover_dir(LargeScalePath.REPORT_DIR)

    @classmethod
    def clear_last_info_except_inventory(cls):
        cls.recover_dir(LargeScalePath.REPORT_DIR)
        all_remote_ip = os.listdir(LargeScalePath.REMOTE_HOST_RESULTS)
        for ip in all_remote_ip:
            remote_info_path = os.path.join(LargeScalePath.REMOTE_HOST_RESULTS, ip)
            for file in os.listdir(remote_info_path):
                if file != ProjectPath.INVENTORY_FILE:
                    os.remove(os.path.join(remote_info_path, file))
