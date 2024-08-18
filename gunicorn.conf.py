def on_starting(server):
    from basic_server.src.app import initialize_scheduler
    initialize_scheduler()

preload_app = True
