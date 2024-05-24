# List of topics to be watched. Messages received will be written to stdout.
topic_prefixes_to_watch = ['']
# Seconds between hearbeat publishes
heartbeat_period = 10

# Volttron address and keys used to create agents
agent_kwargs = {
    # Volttron VIP address
    'address': 'tcp://192.168.128.72:22950',

    # Required keys for establishing an encrypted VIP connection
    'secretkey': '8aIxZNuzaYGDiptENNBulR5D_Aj13qD8qBag5MO_t8A',
    'publickey': 'rg2zKt4OeKxksvTWQh4c6D9ROA-6AgaOcBi0Fdvdn0o',
    'serverkey': 'WzkpIr892tZS1LMNEhxbNFDkzLz3hHwwLhGH2JF4tU8',
    # Don't use the configuration store
    'enable_store': True,
}

