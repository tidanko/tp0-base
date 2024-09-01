docker build -t test .
. ./test.env
python3 validar-input.py "$MESSAGE" "$(docker run --network=tp0_testing_net -e MESSAGE="$MESSAGE" -e PORT=$PORT test)"