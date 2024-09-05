. ./input_validation.env
python3 validar-input.py "$MESSAGE" "$(docker run --rm --network=tp0_testing_net busybox sh -c "echo '$MESSAGE' | nc server $PORT")"
