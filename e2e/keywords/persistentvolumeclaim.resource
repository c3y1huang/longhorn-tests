*** Settings ***
Documentation    PersistentVolumeClaim Keywords

Library    Collections
Library    ../libs/keywords/common_keywords.py
Library    ../libs/keywords/persistentvolumeclaim_keywords.py
Library    ../libs/keywords/volume_keywords.py

*** Keywords ***
Create persistentvolumeclaim ${claim_id} using ${volume_type} volume
    ${claim_name} =    generate_name_with_suffix    claim    ${claim_id}
    create_persistentvolumeclaim    ${claim_name}    ${volume_type}

Create persistentvolumeclaim ${claim_id} using ${volume_type} volume with ${sc_name} storageclass
    ${claim_name} =    generate_name_with_suffix    claim    ${claim_id}
    create_persistentvolumeclaim    ${claim_name}    ${volume_type}    ${sc_name}

Delete persistentvolumeclaim ${claim_id}
    ${claim_name} =    generate_name_with_suffix    claim    ${claim_id}
    delete_persistentvolumeclaim    ${claim_name}

Delete persistentvolumeclaim for volume ${volume_id}
    ${pvc_name} =    generate_name_with_suffix    volume    ${volume_id}
    delete_persistentvolumeclaim    ${pvc_name}
