def register_blueprints(app):
    from app.controllers.auth_controller import auth_bp
    from app.controllers.user_controller import user_bp
    from app.controllers.sesi_controller import sesi_bp
    # from app.controllers.reservasi_controller import reservasi_bp
    from app.controllers.admin_controller import admin_bp
    from app.controllers.wahana_controller import wahana_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(sesi_bp)
    # app.register_blueprint(reservasi_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(wahana_bp)
