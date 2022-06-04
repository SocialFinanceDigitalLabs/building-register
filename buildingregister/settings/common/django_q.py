Q_CLUSTER = {
    'name': 'building-register',
    'workers': 2,
    'recycle': 500,
    'timeout': 600,
    'retry': 660,
    'compress': True,
    'save_limit': 250,
    'queue_limit': 500,
    'cpu_affinity': 1,
    'label': 'Django Q',
    'orm': 'default',
}
