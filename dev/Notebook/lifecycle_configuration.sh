#!/bin/bash

set -e

SCRIPT_VERSION="v5"

## SageMaker Jupyter Notebook
SM_USER=ec2-user
SM_USER_HOME=/home/${SM_USER}
mkdir -p ${SM_USER_HOME}
LOG_FILE=${SM_USER_HOME}/notebook-start.log
SCRIPT_TITLE="Jupyter Notebook"

function log_it() {
    echo "$@" >> ${LOG_FILE}
}

function do_it() {
    local cmd=$1
    shift
    echo "" >> ${LOG_FILE}
    ${cmd} "$@" >> ${LOG_FILE} 2>&1 || echo "ERROR: failed to call: ${cmd} $@" >> ${LOG_FILE}
}

function install_jfrog_cli() {
    echo "--- Installing JFrog CLI"
    curl -sfL https://install-cli.jfrog.io | sh
    chmod +x "$(which jf)"
    jf --version
    echo "JFrog CLI installed at: $(which jf)"
    echo "Done"
}

SECRET_PAYLOAD=
RT_USER=
RT_TOKEN=
RT_HOST=
RT_REPO_PYPI=
RT_REPO_HUGGINGFACE=

function fetch_artifactory_config() {
    if ! [[ -z "${SECRET_PAYLOAD}" ]]; then
        echo "Artifactory config details already fetched, skipping." >&2
        return 0
    fi
    echo "Fetching Artifactory config details." >&2
    SECRET_PAYLOAD="$(aws secretsmanager get-secret-value --secret-id sagemaker-poc-artifactory-details --query SecretString --output text)"
    RT_USER="$(echo "${SECRET_PAYLOAD}" | jq -r .username | sed 's/@/%40/g')"
    RT_TOKEN="$(echo "${SECRET_PAYLOAD}" | jq -r .token)"
    RT_HOST="$(echo "${SECRET_PAYLOAD}" | jq -r .host)"
    RT_REPO_PYPI="$(echo "${SECRET_PAYLOAD}" | jq -r .pypirepo)"
    RT_REPO_HUGGINGFACE="$(echo "${SECRET_PAYLOAD}" | jq -r .huggingfacerepo)"
    echo "Artifactory config details:" >&2
    echo "  Host:  ${RT_HOST}" >&2
    echo "  User:  ${RT_USER}" >&2
    echo "  Token: $(if ! [[ -z "${RT_TOKEN}" ]]; then echo '*****' ; fi)" >&2
    echo "  Repositories:" >&2
    echo "    PyPi: ${RT_REPO_PYPI}" >&2
    echo "    HuggingFaceML: ${RT_REPO_HUGGINGFACE}" >&2
}

function get_pypi_index_url() {
    fetch_artifactory_config
    echo "--- Resolved index-url: https://${RT_USER}:*****@${RT_HOST}/artifactory/api/pypi/${RT_REPO_PYPI}/simple" >&2
    echo "https://${RT_USER}:${RT_TOKEN}@${RT_HOST}/artifactory/api/pypi/${RT_REPO_PYPI}/simple"
}

function setup_pip() {
    echo "--- Setting up pip"
    pip --version
    echo "Pip installed at: $(which pip)"
    local INDEX_URL
    INDEX_URL="$(get_pypi_index_url)"
    pip config --global set global.index-url "${INDEX_URL}"
    echo "Done"
}

function setup_huggingface() {
    echo "--- Setting up HuggingFaceML"
    fetch_artifactory_config
    local HF_ENDPOINT="https://${RT_HOST}/artifactory/api/huggingfaceml/${RT_REPO_HUGGINGFACE}"
    echo "Resolved HuggingFaceML repo endpoint: ${HF_ENDPOINT}"

    echo "Updating env profile with HuggingFace environment settings"
    append_to_env HF_ENDPOINT "${HF_ENDPOINT}"
    append_to_env HUGGING_FACE_HUB_TOKEN "${RT_TOKEN}"
    echo "Done"
}

function setup_jfrog_cli() {
    echo "--- Setting up JFrog CLI"
    fetch_artifactory_config
    export JFROG_CLI_HOME_DIR=${SM_USER_HOME}/.jfrog
    local SERVER_ID=artifactory
    jf config add \
        --url="https://${RT_HOST}" \
        --user="${RT_USER}" \
        --access-token="${RT_TOKEN}" \
        --interactive=false \
        "${SERVER_ID}"
    echo "Setting up repo for PyPi resolution"
    jf pipc --global=true --repo-resolve="${RT_REPO_PYPI}" --server-id-resolve="${SERVER_ID}"
    chown -R ${SM_USER} "${JFROG_CLI_HOME_DIR}"
    echo "Done"
}

function append_to_env() {
    # Based on https://github.com/aws-samples/sagemaker-studio-lifecycle-config-examples/blob/main/scripts/set-proxy-settings/on-jupyter-server-start.sh
    local VAR_NAME="$1"
    local VAR_VALUE="$2"
    echo "Adding environment variable to JFrog env: ${VAR_NAME}" >&2
    append_to_shell_env_file "${VAR_NAME}" "${VAR_VALUE}"
    append_to_jupyter_env_file "${VAR_NAME}" "${VAR_VALUE}"
}

function append_to_shell_env_file() {
    local VAR_NAME="$1"
    local VAR_VALUE="$2"
    local JFROG_ENV_FILE=/etc/profile.d/jfrog-env.sh
    if ! [[ -f ${JFROG_ENV_FILE} ]]; then
        echo "Initializing shell profile for JFrog env in: ${JFROG_ENV_FILE}" >&2
        touch ${JFROG_ENV_FILE}
    fi
    echo "export ${VAR_NAME}=${VAR_VALUE}" >> ${JFROG_ENV_FILE}
}

function append_to_jupyter_env_file() {
    local VAR_NAME="$1"
    local VAR_VALUE="$2"
    local JFROG_ENV_FILE=${SM_USER_HOME}/.ipython/profile_default/startup/00-jfrog-env.py
    if ! [[ -f ${JFROG_ENV_FILE} ]]; then
        echo "Initializing Jupyter profile for JFrog env in: ${JFROG_ENV_FILE}" >&2
        echo "import sys,os,os.path" >  ${JFROG_ENV_FILE}
        echo ""                      >> ${JFROG_ENV_FILE}
    fi
    echo "os.environ['${VAR_NAME}']=\"${VAR_VALUE}\"" >> ${JFROG_ENV_FILE}
}

log_it ">>> Starting ${SCRIPT_TITLE} setup at $(date +%FT%T)"
log_it "Script version: ${SCRIPT_VERSION}"

do_it install_jfrog_cli
do_it setup_pip
do_it setup_huggingface
do_it setup_jfrog_cli

log_it ""
log_it "<<< Finished ${SCRIPT_TITLE} setup at $(date +%FT%T)"
