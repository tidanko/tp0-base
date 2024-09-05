import yaml
import sys

def main():
    if len(sys.argv) != 3 or not sys.argv[2].isnumeric() or int(sys.argv[2]) < 0 or len(sys.argv[1]) < 6 or sys.argv[1][len(sys.argv[1]) - 5:] != '.yaml':
        raise ValueError("The parameters introduced are incorrect. Use: ./generar-compose.sh <file-name> <clients_amount>")


    file_name = sys.argv[1]
    clients_amount = int(sys.argv[2])

    data = {
        'name': 'tp0',
        'services': {
            'server': {
                'container_name': 'server',
                'image': 'server:latest',
                'entrypoint': 'python3 /main.py',
                'environment': ['PYTHONUNBUFFERED=1', 'LOGGING_LEVEL=DEBUG'],
                'networks': ['testing_net'],
                'volumes': ['./server/config.ini:/config.ini'],
            }    
        },
        'networks': {
            'testing_net': {
                'ipam': {
                    'driver': 'default',
                    'config': [{'subnet': '172.25.125.0/24'}]
                }
            }
        },
    }

    for i in range(1, clients_amount + 1):
        new_client = {
            'container_name': f'client{i}',
            'image': 'client:latest',
            'entrypoint': '/client',
            'environment': [f'CLI_ID={i}', 'CLI_LOG_LEVEL=DEBUG'],
            'networks': ['testing_net'],
            'depends_on': ['server'],
            'volumes': ['./client/config.yaml:/config.yaml', './.data:/.data']
        }
        data['services'][f'client{i}'] = new_client
    
    with open(file_name, 'w') as file:
        yaml.dump(data, file, sort_keys=False)

    return

main()