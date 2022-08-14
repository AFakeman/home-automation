#!/usr/bin/env bash

if ! command -v op &> /dev/null; then
    echo -n Vault password:
    read -s password
    echo $password
else
    op get item "Ansible Vault for Home DC" | jq .details.password -rj
fi
