import os

all_client_data = {
    'client_information': {'address': 'ABC 245 Rd,Karachi',
                        'client_name': 'Shahzain Ali',
                        'company_name': 'The Agentive',
                        'country': 'Pakistan',
                        'current_date': '2025-10-30',
                        'due_date': '2025-11-10',
                        'email': 'shahzainalii859@gmail.com'},
    'grand_total': 0.0,
    'items': [{'description': 'AI Chatbot', 'hours': 50.0, 'rate_per_hour': 40.0}],
    'subtotal': 0.0
}

for client in all_client_data:
    print(client)
