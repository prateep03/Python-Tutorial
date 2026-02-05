#!/bin/bash

# Activate virtual environment
venv_name="hf_env"
work_dir="/teamspace/studios/this_studio"

# If python3.11 is not available, install it using apt-get install
# if ! command -f find / -type f -executable -name "python3.11" &> /dev/null; then
#     echo "Python 3.11 not found. Installing Python 3.11..."
#     sudo apt-get install -y python3.11 python3.11-venv python3.11-dev
# fi

if [ "$(echo $VIRTUAL_ENV)" != "$work_dir/virtual_envs/$venv_name" ]; then
    echo "Activating virtual environment: $venv_name"
    source "$work_dir/virtual_envs/$venv_name/bin/activate"
fi

alias install='pip3.11 install --no-cache-dir'

# # install torch with the correct cuda version, check nvcc --version
# install torch --extra-index-url https://download.pytorch.org/whl/cu116 --upgrade
# # install Hugging Face Libraries
# install "transformers==4.26.0" "datasets>=2.14.0" "accelerate==0.16.0" "evaluate==0.4.0" --upgrade
# # install deepspeed and ninja for jit compilations of kernels
# install "deepspeed==0.8.0" ninja --upgrade
# # install additional dependencies needed for training
# install rouge-score nltk py7zr tensorboard
# install dotenv scikit-learn
# install --upgrade pyarrow pandas datasets polars 
# install "huggingface_hub==0.34.3" 
# install "numpy==1.26.4"

# install torch with the correct cuda version, check nvcc --version
install torch --extra-index-url https://download.pytorch.org/whl/cu116 --upgrade
# install Hugging Face Libraries
install "transformers[torch]" "datasets" "accelerate>=1.1.0" "evaluate==0.4.0" --upgrade
# install deepspeed and ninja for jit compilations of kernels
install "deepspeed==0.8.0" ninja --upgrade
# install additional dependencies needed for training
install rouge-score nltk py7zr tensorboard
install huggingface_hub openpyxl dotenv scikit-learn


# Reinstall "numpy>=1.23.0,<2.0.0"
install "numpy>=1.23.0,<2.0.0" --upgrade 
install --force-reinstall pandas pyarrow
install "pydantic<2.0.0"