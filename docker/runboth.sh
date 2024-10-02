# Launch Orthanc
Orthanc ./orthanc/orthanc.json &
sleep 5

ENV_NAME=${ENV_NAME:-ark_mirai_orthanc}
echo "Activating conda environment $ENV_NAME"
conda init --all

# Source the shell initialization script to apply changes
source ~/.bashrc

conda activate $ENV_NAME

# Run regular ark
ark-run mirai &

# Run Orthanc listener
python orthanc/rest_listener.py &

wait