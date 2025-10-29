def register_blueprints(app):
    from app.controllers.auth_controller import auth_bp
    from app.controllers.user_controller import user_bp
    from app.controllers.sesi_controller import sesi_bp
    from app.controllers.reservasi_controller import reservasi_bp
    from app.controllers.admin_controller import admin_bp
    from app.controllers.wahana_controller import wahana_bp
    from app.controllers.pembayaran_controller import pembayaran_bp
    from app.controllers.reservasi_admin_controller import reservasi_admin_bp
    from app.controllers.staff_controller import staff_bp
    from app.controllers.validasi_admin_controller import validasi_admin_bp
    from app.controllers.validasi_staff_controller import validasi_staff_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(sesi_bp)
    app.register_blueprint(reservasi_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(wahana_bp)
    app.register_blueprint(pembayaran_bp)
    app.register_blueprint(reservasi_admin_bp)
    app.register_blueprint(staff_bp)
    app.register_blueprint(validasi_admin_bp)
    app.register_blueprint(validasi_staff_bp)