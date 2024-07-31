log_file_path = r"C:\inetpub\wwwroot\HR-Module\python.log"

try:
    with open(log_file_path, 'w') as log_file:
        log_file.write('Log file created successfully.')
        print(f'Log file created at: {log_file_path}')
except Exception as e:
    print(f'Error creating log file: {str(e)}')
