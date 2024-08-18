def on_starting(server):
    from basic-server.src.app import initialize_scheduler
    initialize_scheduler()

preload_app = True
