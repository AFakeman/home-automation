#!/usr/bin/env bash

if ! command -v op &> /dev/null; then
    echo -n Vault password:
    read -s password
    echo $password
else
    op item get "Ansible Vault for Home DC" --format json | jq -r '.fields[]|select(.id=="password").value'
fi
