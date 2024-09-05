docker build -t input_validation .
. ./input_validation.env
python3 validar-input.py "$MESSAGE" "$(docker run --network=tp0_testing_net -e MESSAGE="$MESSAGE" -e PORT=$PORT input_validation)"
