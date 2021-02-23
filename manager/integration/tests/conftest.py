import pytest

from kubernetes import client as k8sclient, config as k8sconfig
from kubernetes.client import Configuration

from common import get_longhorn_api_client, \
    NODE_CONDITION_MOUNTPROPAGATION, CONDITION_STATUS_TRUE
from common import wait_for_node_mountpropagation_condition
from common import check_longhorn, check_csi_expansion


INCLUDE_BASE_IMAGE_OPT = "--include-base-image-test"
SKIP_RECURRING_JOB_OPT = "--skip-recurring-job-test"
INCLUDE_INFRA_OPT = "--include-infra-test"
INCLUDE_STRESS_OPT = "--include-stress-test"
INCLUDE_UPGRADE_OPT = "--include-upgrade-test"

UPGRADE_LH_MANAGER_REPO_URL = "--upgrade-lh-manager-repo-url"
UPGRADE_LH_MANAGER_REPO_BRANCH = "--upgrade-lh-manager-repo-branch"
UPGRADE_LH_MANAGER_IMAGE = "--upgrade-lh-manager-image"
UPGRADE_LH_ENGINE_IMAGE = "--upgrade-lh-engine-image"
UPGRADE_LH_INSTANCE_MANAGER_IMAGE = "--upgrade-lh-instance-manager-image"
UPGRADE_LH_SHARE_MANAGER_IMAGE = "--upgrade-lh-share-manager-image"


def pytest_addoption(parser):
    parser.addoption(INCLUDE_BASE_IMAGE_OPT, action="store_true",
                     default=False, help="include base image tests")

    parser.addoption(SKIP_RECURRING_JOB_OPT, action="store_true",
                     default=False,
                     help="skip recurring job test or not")

    parser.addoption(INCLUDE_INFRA_OPT, action="store_true",
                     default=False,
                     help="include infra tests (default: False)")

    parser.addoption(INCLUDE_STRESS_OPT, action="store_true",
                     default=False,
                     help="include stress tests (default: False)")

    parser.addoption(INCLUDE_UPGRADE_OPT, action="store_true",
                     default=False,
                     help="include upgrade tests (default: False)")

    longhorn_manager_repo_url =\
        "https://github.com/longhorn/longhorn-manager.git"
    parser.addoption(UPGRADE_LH_MANAGER_REPO_URL, action="store",
                     default=longhorn_manager_repo_url,
                     help='''set longhorn-manger repo url, this will be used
                     to generate longhorn yaml manifest for test_upgrade
                     (default:
                     https://github.com/longhorn/longhorn-manager.git)''')

    parser.addoption(UPGRADE_LH_MANAGER_REPO_BRANCH, action="store",
                     default="master",
                     help='''set longhorn-manger repo branch, this will be used
                     to generate longhorn yaml manifest for test_upgrade
                     (default: master)''')

    parser.addoption(UPGRADE_LH_MANAGER_IMAGE, action="store",
                     default="longhornio/longhorn-manager:master",
                     help='''set custom longhorn-manger image, this image will
                     be used in test_upgrade
                     (default: longhornio/longhorn-manager:master)''')

    parser.addoption(UPGRADE_LH_ENGINE_IMAGE, action="store",
                     default="longhornio/longhorn-engine:master",
                     help='''set custom longhorn-engine image, this image will
                     be used in test_upgrade
                     (default: longhornio/longhorn-engine:master)''')

    parser.addoption(UPGRADE_LH_INSTANCE_MANAGER_IMAGE, action="store",
                     default="longhornio/longhorn-instance-manager:master",
                     help='''set custom longhorn-instance-manager image, this
                     image will be used in test_upgrade
                     (default: longhornio/longhorn-instance-manager:master)
                     ''')

    parser.addoption(UPGRADE_LH_SHARE_MANAGER_IMAGE, action="store",
                     default="longhornio/longhorn-share-manager:master",
                     help='''set custom longhorn-share-manager image, this image
                     will be used in test_upgrade
                     (default: longhornio/longhorn-share-manager:master)''')


def pytest_collection_modifyitems(config, items):
    c = Configuration()
    c.assert_hostname = False
    Configuration.set_default(c)
    k8sconfig.load_incluster_config()
    core_api = k8sclient.CoreV1Api()

    check_longhorn(core_api)

    include_base_image = config.getoption(INCLUDE_BASE_IMAGE_OPT)
    if not include_base_image:
        skip_base_image = pytest.mark.skip(reason="set " +
                                                  INCLUDE_BASE_IMAGE_OPT +
                                                  " option to run")
        for item in items:
            if "baseimage" in item.keywords:
                item.add_marker(skip_base_image)

    if config.getoption(SKIP_RECURRING_JOB_OPT):
        skip_upgrade = pytest.mark.skip(reason="remove " +
                                               SKIP_RECURRING_JOB_OPT +
                                               " option to run")
        for item in items:
            if "recurring_job" in item.keywords:
                item.add_marker(skip_upgrade)

    csi_expansion_enabled = check_csi_expansion(core_api)
    if not csi_expansion_enabled:
        skip_csi_expansion = pytest.mark.skip(reason="environment is not " +
                                                     "using csi expansion")
        for item in items:
            if "csi_expansion" in item.keywords:
                item.add_marker(skip_csi_expansion)

    all_nodes_support_mount_propagation = True
    for node in get_longhorn_api_client().list_node():
        node = wait_for_node_mountpropagation_condition(
            get_longhorn_api_client(), node.name)
        if "conditions" not in node.keys():
            all_nodes_support_mount_propagation = False
        else:
            conditions = node.conditions
            for key, condition in conditions.items():
                if key == NODE_CONDITION_MOUNTPROPAGATION and \
                        condition.status != CONDITION_STATUS_TRUE:
                    all_nodes_support_mount_propagation = False
                    break
        if not all_nodes_support_mount_propagation:
            break

    if not all_nodes_support_mount_propagation:
        skip_upgrade = pytest.mark.skip(reason="environment does not " +
                                               "support base image")
        skip_node = pytest.mark.skip(reason="environment does not " +
                                            "support mount disk")

        for item in items:
            # Don't need to add skip marker for Base Image twice.
            if include_base_image and "baseimage" in item.keywords:
                item.add_marker(skip_upgrade)
            elif "mountdisk" in item.keywords:
                item.add_marker(skip_node)

    if not config.getoption(INCLUDE_INFRA_OPT):
        skip_infra = pytest.mark.skip(reason="include " +
                                      INCLUDE_INFRA_OPT +
                                      " option to run")

        for item in items:
            if "infra" in item.keywords:
                item.add_marker(skip_infra)

    if not config.getoption(INCLUDE_STRESS_OPT):
        skip_stress = pytest.mark.skip(reason="include " +
                                       INCLUDE_STRESS_OPT +
                                       " option to run")

        for item in items:
            if "stress" in item.keywords:
                item.add_marker(skip_stress)

    if not config.getoption(INCLUDE_UPGRADE_OPT):
        skip_upgrade = pytest.mark.skip(reason="include " +
                                        INCLUDE_UPGRADE_OPT +
                                        " option to run")

        for item in items:
            if "upgrade" in item.keywords:
                item.add_marker(skip_upgrade)
