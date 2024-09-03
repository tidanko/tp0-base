docker build -t input_validating .
. ./input_validating.env
python3 validar-input.py "$MESSAGE" "$(docker run --network=tp0_testing_net -e MESSAGE="$MESSAGE" -e PORT=$PORT input_validating)"