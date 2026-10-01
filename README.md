# SmartClinic

An academic desktop application for managing customers, sellers, products and purchases with Python, Tkinter and MySQL. The graphical interface and data-access classes are present; database provisioning is incomplete in this repository.

## Local setup

Use Python 3, MySQL and a graphical desktop with Tkinter installed. Create and activate a virtual environment, then:

```bash
python -m pip install -r requirements.txt
cp secreto.env.example secreto.env
```

On Windows, copy the example file using your file manager or `Copy-Item`. Edit `secreto.env` with your local database connection values. That file is ignored by Git; never commit credentials.

The MySQL database must already exist and match the tables and columns referenced in `src/*_dao.py`. **No SQL schema, migration or reproducible database bootstrap is currently tracked**, so a fresh installation is not yet complete.

## Entry points

```bash
python interface/interface.py
```

The GUI attempts to connect at startup and reports unavailable database access. A separate customer-management CLI is available:

```bash
python src/main.py
```

## Organization

- `interface/interface.py`: Tkinter GUI.
- `src/db.py`: environment loading and connection lifecycle.
- `src/cliente_dao.py`, `vendedor_dao.py`, `produto_dao.py`, `compra_dao.py`: database operations.

## Validation and next steps

During the portfolio audit, paths and Python syntax were checked. MySQL integration and desktop interactions were not executed. This is a course project, not a verified production clinic system.

The next engineering milestones are a versioned schema, integration tests, purchase input validation, transaction/concurrency checks and consistent monetary precision. Patient care, authentication and a clinical records system are outside the current implementation.

## License

[MIT](LICENSE).
